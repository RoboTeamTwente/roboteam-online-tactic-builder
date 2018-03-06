"""
This file contains all the Serializers that are responsible for enforcing
the protocol. The ProtocolSerializer is the root of the protocol and will
deligate all the action to the appropriate Serializers to let them handle
their part.
"""

from rest_framework.serializers import Serializer, ChoiceField, DictField


class ProtocolSerializer(Serializer):
    """
    The ProtocolSerializer is used to validate incoming JSON object agains the
    protocol used for communication over the websocket.
    """

    PROTOCOL_CHOICES = [
        ("SIM", "start_sim"),
        ("STOP", "stop_sim")
    ]

    action = ChoiceField(choices=PROTOCOL_CHOICES)
    values = DictField()

    def start_sim(self, values):
        """
        Validator for the SIM action.
        :param values: The values passed by the client with the action.
        """
        serializer = StartSimulatorSerializer(data=values)
        serializer.is_valid(raise_exception=True)
        return values

    def stop_sim(self, values):
        """
        Validator for the STOP action.
        :param values: The values passed by the client with the action.
        """
        # For now the STOP action does not take any values
        # Later these might include things like which simulator to stop
        return values

    def action_method(self, data=None):
        """
        Get the method name of the selected action
        :param data: The validated data
        :return: The action method name
        """

        data = self.validated_data if data is None else data
        choices = ProtocolSerializer.PROTOCOL_CHOICES
        return [x for x in choices if x[0] == data["action"]][
            0][1]

    def validate(self, data):
        """
        Deligate the validation of the specific messages to the appropriate
        serializer.
        :param data: The data to be validated.
        :return: The validated data.
        """

        # Execute the appropriate validator for this protocol action
        method = self.action_method(data=data)
        data["values"] = getattr(self, method)(data["values"])

        return data


class StartSimulatorSerializer(Serializer):
    """
    The StartSimulatorSerializer is used to validate the values given with a SIM
    protocol message.
    """

    # For now only the behavior3 is needed to start the simulator, later a
    # 'level' field might be added to indicate which setup should be used in
    # the simulator.
    tree = DictField()
