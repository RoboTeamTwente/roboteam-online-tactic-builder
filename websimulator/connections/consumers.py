"""
This file contains all the Consumers ( SyncConsumers as in
channels.readthedocs.io --> Consumers) that will handle all the asynchonous
connections and all the asynchronous background tasks.
"""

import json
import os
import signal
import subprocess
import time
from enum import Enum
from pathlib import Path

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer, SyncConsumer

from websimulator import settings
from .serializers import ProtocolSerializer


class WsConnectionConsumer(JsonWebsocketConsumer):
    """
    Websocket consumer that will be created for each individual connection.
    It will handle the incoming messages, review them using the appropriate
    serializer and pass the message on to the protocol executer. It will
    also handle the incoming messages from background tasks.
    """

    class ErrorCodes:
        """
        In case something goes wrong it is appropriate to close the
        connection but let the user know what went wrong.
        """
        protocol_error = 3000
        tree_error = 3001

    def __init__(self, *args, **kwargs):
        """
        Override to create a ProtocolExecuter and keep it seperate form the
        consumer.
        """
        super().__init__(*args, **kwargs)
        self.executer = ProtocolExecuter(self)

    def connect(self):
        """
        Handle the incoming connection. For now all connections are accepted.
        """
        self.accept()

    def receive_json(self, content, **kwargs):
        """
        Filters the json through a serializer to make sure only actions in the
        protocol are accepted. Next there will be acted upon the result and
        long during tasks will be send to a background task.
        :param content: Json object with the send json from the client.
        :param kwargs: Mandatory python object.
        """

        # Validate that the json is following the protocol
        serializer = ProtocolSerializer(data=content)
        if serializer.is_valid():
            # Run the appropriate handler for the action and pass it the values
            getattr(self.executer, serializer.action_method())(
                serializer.validated_data["values"])
        else:
            # Close connection with a 'protocol error'
            self.send_json({
                "code": WsConnectionConsumer.ErrorCodes.protocol_error,
                "errors": serializer.errors
            }, close=True)

    def forward_to_client(self, message):
        """
        Forwards messages from the background tasks to the client.
        :param message: The message (dict) in which the json resides that the
        background process wants to end up at the client.
        """
        self.send_json({
            "body": message["json"]
        })


class ProtocolExecuter():
    """
    The protocol executer receives messages that follow the protocol,
    the consumer already validated this. The executer makes sure that
    appropriate action is being taken accordingly.
    """

    def __init__(self, consumer: WsConnectionConsumer):
        """
        Remain a connection to the consumer to make communication possible.
        :param consumer: The consumer that started the simulator.
        """
        super().__init__()
        self.consumer = consumer

    def start_sim(self, values: dict):
        """
        The action that will start the simulator.
        :param values: The action values needed for the simulator.
        """
        async_to_sync(self.consumer.channel_layer.send)(
            "simulator",
            {
                "type": "start",
                "channel_name": self.consumer.channel_name,
                "values": values
            }
        )

    def stop_sim(self, values: dict):
        # Dummy for later implementation
        pass


class ListenerConsumer(SyncConsumer):

    def listen(self, message):
        print("Listener: Start the strategy")
        async_to_sync(self.channel_layer.send)(
            "simulator",
            {
                "type": "run"
            }
        )

        time.sleep(10)
        print("Listener: Terminate the simulator")
        async_to_sync(self.channel_layer.send)(
            "simulator",
            {
                "type": "stop",
            }
        )


class State(Enum):
    READY = 1
    PREPARED = 2
    RUNNING = 3


simulator_state = State.READY
tactic_pid = -1
grsim_pid = -1
ros_pid = -1


def printSimState():
    print("simulator_state: {0}".format(simulator_state))
    print("tactic_pid: {0}".format(tactic_pid))
    print("ros_pid: {0}".format(ros_pid))
    print("grsim_pid: {0}".format(grsim_pid))


class SimulateConsumer(SyncConsumer):
    """
    Background consumer that will start the simulator and report back to the
    client via the forward_to_client method of the connected websocket.
    """

    def start(self, message):
        if simulator_state != State.READY:
            print("Simulator: Already running")
            return
        print("Simulator: Start the preparation")
        edit_tree(message["values"])
        global ros_pid
        global grsim_pid
        ros_pid = start_ros().pid
        grsim_pid = start_grsim().pid

        printSimState()

        print("Simulator: Message the listener")
        global simulator_state
        simulator_state = State.PREPARED
        async_to_sync(self.channel_layer.send)(
            "listener",
            {
                "type": "listen",
                "channel_name": message["channel_name"],
            }
        )

    def run(self, message):
        print("Simulator: Run the tactic")
        printSimState()
        global tactic_pid
        tactic_pid = start_tactic().pid
        print("Simulator: The simulation has started")
        global simulator_state
        simulator_state = State.RUNNING

    def stop(self, message):
        print("Simulator: Stop the simulator")
        printSimState()
        os.killpg(os.getpgid(tactic_pid), signal.SIGTERM)
        os.killpg(os.getpgid(ros_pid), signal.SIGTERM)
        os.killpg(os.getpgid(grsim_pid), signal.SIGTERM)
        print("Simulator: The simulator was stopped")
        global simulator_state
        simulator_state = State.READY


def edit_tree(values):
    """
    Parse the new tree and insert this into the current project
    Assumes a project rtt_tactics.b3 is already available in the mentioned location
    :param values: the newly created tree

    """
    tree = values["tree"]
    tree["title"] = settings.TREE_NAME

    result = {'data': {'trees': [tree]}}

    project_location = str(
        Path.home()) + '/catkin_ws/src/roboteam_tactics/src/trees/projects/' + settings.PROJECT_NAME + ".b3"

    new_project = open(project_location, 'w')
    new_project.write(json.dumps(result))
    new_project.close()

    return subprocess.run("cd ~/catkin_ws && catkin_make", shell=True,
                          stdout=open(os.devnull, 'w'))


def start_ros():
    """
    Start ROS

    """
    return subprocess.Popen("roslaunch roboteam_tactics RTTCore_grsim.launch",
                            stdout=open(os.devnull, 'w'),
                            shell=True, preexec_fn=os.setsid)


def start_grsim():
    """
    Start grSim

    """
    return subprocess.Popen("~/catkin_ws/grSim/bin/grsim",
                            stdout=open(os.devnull, 'w'),
                            shell=True, preexec_fn=os.setsid)


def start_tactic():
    """
    Start the predefined tactic

    """
    return subprocess.Popen("rosrun roboteam_tactics TestX " + settings.PROJECT_NAME + "/" + settings.TREE_NAME,
                            stdout=open(os.devnull, 'w'),
                            shell=True, preexec_fn=os.setsid)
