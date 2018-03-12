"""
This file contains all the Consumers ( SyncConsumers as in
channels.readthedocs.io --> Consumers) that will handle all the asynchonous
connections and all the asynchronous background tasks.
"""

import os
import threading
import json

from pathlib import Path

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer, SyncConsumer

from connections.exceptions import TreeException
from .serializers import ProtocolSerializer, SimValuesSerializer, CustomNodesSerializer


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
                "type": "simulate",
                "channel_name": self.consumer.channel_name,
                "values": values
            }
        )

    def stop_sim(self, values: dict):
        # Dummy for later implementation
        pass


class SimulateConsumer(SyncConsumer):
    """
    Background consumer that will start the simulator and report back to the
    client via the forward_to_client method of the connected websocket.
    """

    def simulate(self, message):
        """
        Message to start the simulator. The tree must be provided in the
        message as well as the channel name to be able to return messages.

        TODO: 0.1 Improve this very ugy, threaded implementation, to a nice one.
        :param message: The dictionary that was passed to the background by
        the ProtocolExecuter.
        """

        edit_tree(message["values"])

        ros_thread = threading.Thread(target=start_ros, name="ros")
        ros_thread.start()
        async_to_sync(self.channel_layer.send)(
            message["channel_name"],
            {
                "type": "forward.to.client",
                "json": {"text": "Started ROS"}
            }
        )
        grsim_thread = threading.Thread(target=start_grsim, name="grsim")
        grsim_thread.start()
        async_to_sync(self.channel_layer.send)(
            message["channel_name"],
            {
                "type": "forward.to.client",
                "json": {"text": "Started grSim"}
            }
        )
        tactic_thread = threading.Thread(target=start_tactic, name="tactic")
        tactic_thread.start()
        async_to_sync(self.channel_layer.send)(
            message["channel_name"],
            {
                "type": "forward.to.client",
                "json": {"text": "Started tactic"}
            }
        )


def edit_tree(values):
    """
    Parse the new tree and insert this into the current project
    Assumes a project rtt_sander.b3 is already available in the mentioned location
    with the right structure
    :param values: the newly created tree

    """
    tree = values["tree"]

    custom_nodes = tree["custom_nodes"]
    del tree["custom_nodes"]

    tree["title"] = "root"

    project_location = str(Path.home()) + '/catkin_ws/src/roboteam_tactics/src/trees/projects/rtt_sander.b3'
    current_project = open(project_location, 'r')

    new_data = ''
    for line in current_project:
        new_data += line

    current_project_json = json.loads(new_data)
    current_project_json['data']['trees'] = [tree]
    current_project_json['data']['custom_nodes'] = custom_nodes

    new_project = open(project_location, 'w')
    new_project.write(json.dumps(current_project_json))

    os.system("cd ~/catkin_ws && catkin_make")


def start_ros():
    """
    Start ROS

    TODO: Remove this as part of 0.1
    """
    os.system("roslaunch roboteam_tactics RTTCore_grsim.launch")


def start_grsim():
    """
    Start grSim

    TODO: Remove this as part of 0.1
    """
    os.system("~/catkin_ws/grSim/bin/grsim")


def start_tactic():
    """
    Start the predefined tactic

    TODO: Remove this as part of 0.1
    """
    os.system("rosrun roboteam_tactics TestX rtt_sander/root")
