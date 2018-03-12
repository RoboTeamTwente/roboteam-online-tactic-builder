"""
This file contains all the Serializers that are responsible for enforcing
the protocol. The ProtocolSerializer is the root of the protocol and will
deligate all the action to the appropriate Serializers to let them handle
their part.
"""

from rest_framework.serializers import Serializer, ChoiceField, DictField, CharField, ListField


class TreeSerializer(Serializer):
    """
    The TreeSerializer is used to validate incoming JSON objects against the
    minimal requirements of a tree.
    """

    root = CharField()
    nodes = DictField()

    def validate_title(self, data):
        data["title"] = "root"
        return data


class CustomNodesSerializer(Serializer):
    """
    The CustomNodesSerializer is used to validate the JSON object against the
    minimal requirements of a custom nodes section.
    """

    custom_nodes = ListField()

class TreeRootSerializer(Serializer):
    """

    """
    tree = DictField()

class ProtocolSerializer(Serializer):
    """
    The ProtocolSerializer is used to validate incoming JSON object against the
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
        tr_serializer = TreeRootSerializer(data=values)
        tr_serializer.is_valid(raise_exception=True)
        values = tr_serializer.validated_data["tree"]

        tree_serializer = TreeSerializer(data=values)
        cn_serializer = CustomNodesSerializer(data=values)
        tree_serializer.is_valid(raise_exception=True)
        cn_serializer.is_valid(raise_exception=True)

        return {
            "tree": tree_serializer.validated_data,
            "custom_nodes": cn_serializer.validated_data["custom_nodes"]
        }

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
