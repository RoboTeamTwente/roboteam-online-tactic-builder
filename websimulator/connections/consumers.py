"""
This file contains all the Consumers ( SyncConsumers as in
channels.readthedocs.io --> Consumers) that will handle all the asynchonous
connections and all the asynchronous background tasks.
"""

import json
import os
import signal
import subprocess
from datetime import datetime, timedelta
import socket
import struct
import shutil
from enum import Enum
from pathlib import Path

import time

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer, SyncConsumer

from websimulator import settings
from .serializers import ProtocolSerializer
from .protobuf import messages_robocup_ssl_wrapper_pb2 as ssl_wrapper


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


def robot_list(team_dict: dict, team: int) -> list:
    """
    Transforms the backend way of presentation of a frame to the front end
    way of presentation of a frame regarding the robots.
    :param team_dict: The dictionary with the players of one team.
    :param team: Team id.
    :return: The list of all the robots of both teams.
    """
    res = []
    for key in team_dict.keys():
        res.append({
            "team": team,
            "id": key,
            "x": team_dict[key]["x"],
            "y": team_dict[key]["y"],
            "orientation": team_dict[key]["orientation"]
        })
    return res


def post_process(frame: dict) -> dict:
    """
    Change the form of the data so the front end can be as lightweight as
    possible.
    :param frame: The resulting frame data.
    :return: The resulting data format.
    """
    frame["robots"] = []
    frame["robots"].extend(robot_list(frame["yellow_robots"], 0))
    frame["robots"].extend(robot_list(frame["blue_robots"], 1))
    del frame["yellow_robots"]
    del frame["blue_robots"]
    return frame


def update(frame: dict, commit: ssl_wrapper.SSL_WrapperPacket) -> dict:
    """
    This update function is used to merge the 4 different detection frames
    that is returned by grSim. grSim will send for every frame 4 packets
    with different and double parts of the detection. Using this function
    the data is merged and stored in a single dictionary. The function will
    only update values that have not been provided yet.
    :param frame: The previous state of the stored knowledge of the frame
    :param commit: The new packet that possible provides new information
    about the frame state
    :return: The new state of the stored knowledge of the frame
    """
    detection = commit.detection

    # In case the previous game state was empty, the basic data will be loaded
    if "frame_number" not in frame:
        frame["frame_number"] = detection.frame_number
        frame["ball"] = {}
        frame["yellow_robots"] = {}
        frame["blue_robots"] = {}

    # If there is a ball in the detection and the ball was not loaded, then load
    if len(detection.balls) > 0 and frame["ball"] == {}:
        frame["ball"] = {
            "x": detection.balls[0].x,
            "y": detection.balls[0].y,
            "z": detection.balls[0].z
        }

    # Take the states of the robots and store them in the frame
    for robot in detection.robots_yellow:
        if robot.robot_id not in frame["yellow_robots"]:
            frame["yellow_robots"][robot.robot_id] = {
                "x": robot.x,
                "y": robot.y,
                "orientation": robot.orientation
            }
    for robot in detection.robots_blue:
        if robot.robot_id not in frame["blue_robots"]:
            frame["blue_robots"][robot.robot_id] = {
                "x": robot.x,
                "y": robot.y,
                "orientation": robot.orientation

            }

    return frame


class SimulationStatus(Enum):
    READY = 1
    SUBMITTED = 2
    QUEUED = 3
    GENERATING = 4
    STARTING_SIMULATION = 5
    SIMULATING = 6
    BUFFERING = 7
    FINISHED = 8


def send_simulation_status(channel_layer, channel_name: str, status: SimulationStatus):
    async_to_sync(channel_layer.send)(
        channel_name,
        {
            "type": "forward.to.client",
            "json": {
                "simulator_status": status.value
            }
        }
    )


class ListenerConsumer(SyncConsumer):
    """
    Consumer that will be responsible for managing the simulation after it
    has been started. It will listen to the data and return it to the client
    and it will check on the game state and act accordingly.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the Consumer following the standard Channels way, however
        we add a member field for the socket.
        """
        super().__init__(*args, **kwargs)
        self._initialize()

    def _initialize(self):
        """
        Resets all the variable to the initial listen state.
        """
        self.socket = None
        self.buffer = []
        self.last_frame_number = 0
        self.frame = {}

    def _setup_socket(self, channel_name: str):
        """
        Creates a socket that is able to receive data from grSim. As soon as
        the socket is created the SimulatorConsumer is notified that it is
        allowed to start the tactic.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(settings.SERVER_ADDRESS)
        group = socket.inet_aton(settings.MULTICAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.socket.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            mreq
        )

        print("Listener: Start the strategy")
        async_to_sync(self.channel_layer.send)(
            "simulator",
            {
                "type": "run",
                "channel_name": channel_name
            }
        )

    def _shutdown(self, channel_name: str):
        """
        Flush the buffer and close the socket connection and tell the
        simulator to stop
        ROS and
        grSim.
        """
        if len(self.buffer) > 0:
            self._send_buffered(channel_name)

        self.socket.close()

        print("Listener: Terminate the simulator")
        async_to_sync(self.channel_layer.send)(
            "simulator",
            {
                "type": "stop",
                "channel_name": channel_name
            }
        )

    def _send_buffered(self, channel_name: str):
        """
        Sends the data that has been buffered to the client.
        :param channel_name: The channel name to send back to the client.
        :param buffer: The buffered data that has to be send.
        """
        async_to_sync(self.channel_layer.send)(
            channel_name,
            {
                "type": "forward.to.client",
                "json": {
                    "simulator_output": self.buffer
                }
            }
        )
        self.buffer = []

    def _receive_frame(self):
        """
        Receives data until the frame number is different from the last
        processed frame. When this point is reached the newly received data
        will be saved in a new frame. The old frame will be post-processed
        and added to the buffer.
        :return: The received and processed frame.
        """
        while True:
            data, _ = self.socket.recvfrom(settings.RECEIVE_SIZE)
            packet = ssl_wrapper.SSL_WrapperPacket()
            packet.ParseFromString(data)

            if packet.HasField("detection"):
                if self.last_frame_number != packet.detection.frame_number \
                        and self.frame != {}:
                    result = self.frame
                    self.buffer.append(post_process(result))
                    self.frame = update({}, packet)
                    self.last_frame_number = packet.detection.frame_number
                    break
                self.frame = update(self.frame, packet)
        return result

    def listen(self, message):
        """
        This message is received and will initialize, execute and close the
        listening to the simulator. The data will be listened to, filtered,
        squashed, buffered and lastly forwarded to the client.

        Later on the game state must not only be saved, but also analyzed for potential end states.
        :param message: The message containing information about the client
        and its reply channel.
        """
        self._initialize()
        self._setup_socket(message["channel_name"])

        started = datetime.now()
        while datetime.now() < started + timedelta(
                seconds=settings.MAX_SIMULATION_TIME):
            frame = self._receive_frame()

            # Do something with the game state

            if len(self.buffer) >= settings.BUFFER_SIZE:
                self._send_buffered(message["channel_name"])

        self._shutdown(message["channel_name"])


class State(Enum):
    """
    The state of the simulator. Which can be either ready to start a new
    simulation, currently busy preparing a simulation or currently running a
    simulation.
    """
    READY = 1
    PREPARED = 2
    RUNNING = 3


"""
The variable that will hold the state. This is thread safe as the simulator 
will be ran in a completely separate process.
"""
simulator_state = State.READY
"""
These variables will hold the process id's across this simulation so they 
can later be retrieved and killed.
"""
tactic_pid = -1
grsim_pid = -1


class SimulateConsumer(SyncConsumer):
    """
    Background consumer that will prepare, start and close the simulator.
    """

    def start(self, message):
        """
        Starts the simulator flow. Preparing the tree into C++ and starting
        ros and grSim, after that it will give responsibility to the listener.
        :param message: The standard consumer message.
        """
        global simulator_state
        global grsim_pid

        # TODO: store this simulation request in a queue
        if simulator_state != State.READY:
            print("Simulator: Already running")
            return

        # Prepare the C++ and start ROS and grSim
        print("Simulator: Start the preparation")

        assignment_id = message["values"]["assignment_id"]

        send_simulation_status(self.channel_layer, message["channel_name"], SimulationStatus.GENERATING)
        edit_tree(message["values"])

        send_simulation_status(self.channel_layer, message["channel_name"], SimulationStatus.STARTING_SIMULATION)

        # --- set assignment ID ---
        print("Simulator: writing assignment id to mainwindow.cpp")
        # define path to file
        file_path = os.path.expanduser("~/catkin_ws/grSim/src/mainwindow.cpp")
        from_file = open(file_path, mode="r")
        # remove first line
        from_file.readline()
        # read rest of the file
        contents = from_file.readlines()
        # new first line
        line = "#define ASSIGNMENT_ID " + assignment_id + "\n"
        # remove original file
        os.remove(file_path)
        # open new file
        to_file = open(file_path, mode="w")
        # write new first line
        to_file.write(line)
        # write the rest of the original file
        to_file.writelines(contents)
        to_file.close()
        print("Simulator: making grSim")
        subprocess.Popen("cd ~/catkin_ws/grSim/build && make", shell=True).wait()

        # --- set assignment ID ---

        grsim_pid = subprocess.Popen("~/catkin_ws/grSim/bin/grsim",
                                     shell=True,
                                     preexec_fn=os.setsid).pid

        # Delegate responsibility to the ListenConsumer
        print("Simulator: Message the listener")
        simulator_state = State.PREPARED
        async_to_sync(self.channel_layer.send)(
            "listener",
            {
                "type": "listen",
                "channel_name": message["channel_name"],
            }
        )

    def run(self, message):
        """
        Run the generated tactic in the simulator.
        :param message: Standard message of the consumer.
        """
        global tactic_pid
        global keeper_pid
        global simulator_state

        print("Simulator: Run the tactic")

        tactic_pid = subprocess.Popen("roslaunch roboteam_tactics GUITactic.launch",
                                      shell=True,
                                      preexec_fn=os.setsid).pid
        print("Simulator: The simulation has started")

        send_simulation_status(self.channel_layer, message["channel_name"], SimulationStatus.SIMULATING)
        simulator_state = State.RUNNING

    def stop(self, message):
        """
        Stop the simulator and all the related processes.
        :param message: Standard consumer message.
        """
        global simulator_state

        print("Simulator: Stop the simulator")
        os.killpg(os.getpgid(tactic_pid), signal.SIGTERM)
        os.killpg(os.getpgid(grsim_pid), signal.SIGTERM)

        send_simulation_status(self.channel_layer, message["channel_name"], SimulationStatus.FINISHED)

        print("Simulator: The simulator was stopped")
        simulator_state = State.READY


def edit_tree(values):
    """
    Parse the new tree and insert this into the current project
    Assumes a project rtt_tactics.b3 is already available in the mentioned
    location.
    :param values: the newly created tree.

    """
    tree = values["tree"]
    tree["title"] = settings.TREE_NAME

    #For every node, change it's title to the name of the node and append a number
    nodecounter = 0;
    for node in tree["nodes"]:
        node_json = tree["nodes"][node]
        node_json["title"] = node_json["name"] + "_" + str(nodecounter)
        nodecounter += 1


    result = {'data': {'trees': [tree]}}

    project_location = str(
        Path.home()) + '/catkin_ws/src/roboteam_tactics/src/trees/projects/' + settings.PROJECT_NAME + ".b3"

    new_project = open(project_location, 'w')
    new_project.write(json.dumps(result))
    new_project.close()

    return subprocess.run("cd ~/catkin_ws && catkin_make",
                          shell=True,
                          )
