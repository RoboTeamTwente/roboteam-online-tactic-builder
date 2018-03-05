import os
import threading

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer, SyncConsumer

from .serializers import ProtocolSerializer


class WsConnectionConsumer(JsonWebsocketConsumer):
    class ErrorCodes:
        protocol_error = 3000

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
                "channel_name": self.consumer.channel_name
            }
        )

    def stop_sim(self, values: dict):
        pass


class SimulateConsumer(SyncConsumer):

    def simulate(self, message):
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


def start_ros():
    os.system("roslaunch roboteam_tactics RTTCore_grsim.launch")


def start_grsim():
    os.system("~/catkin_ws/grSim/bin/grsim")


def start_tactic():
    os.system("rosrun roboteam_tactics TestX GoToPos int:ROBOT_ID=2 "
              "double:xGoal=-2 double:yGoal=-2")
