from collections import OrderedDict

from django.test import TestCase

from connections.serializers import *


class ProtocolSerializerTest(TestCase):
    """
    Tests to ensure the serializers verify the correct data
    """

    def test_root_presence(self):
        """
        Test whether a tree is correct when there is no defined root node
        """
        data = {
            "action": "SIM",
            "values": {
                "tree": {
                    "nodes": {

                    }
                }
            }
        }

        serializer = ProtocolSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_nodes_presence(self):
        """
        Test whether the tree contains a nodes dictionary
        """
        data = {
            "action": "SIM",
            "values": {
                "tree": {
                    "root": "x"
                }

            }
        }
        serializer = ProtocolSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_tree_presence(self):
        """
        Test whether there is a tree in the values dictionary
        """
        data = {
            "action": "SIM",
            "values": {

            }
        }
        serializer = ProtocolSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_sim(self):
        """
        Test whether a tree with all the right data is valid
        """
        data = {
            "action": "SIM",
            "values": {
                "tree": {
                    "nodes": {

                    },
                    "root": "x"
                }
            }
        }
        serializer = ProtocolSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["action"], "SIM")
        self.assertEqual(type(serializer.validated_data["values"]), OrderedDict)
        self.assertEqual(type(serializer.validated_data["values"]["tree"]),
                         OrderedDict)

    def test_stop(self):
        """
        Test whether the stop data is valid
        """
        data = {
            "action": "STOP",
            "values": {

            }
        }
        serializer = ProtocolSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["action"], "STOP")
        self.assertEqual(type(serializer.validated_data["values"]), dict)

    def test_action_presence(self):
        """
        Test whether there is an action present in the data
        """
        data = {
            "values": {

            }
        }
        serializer = ProtocolSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_values_presence(self):
        """
        Test whether there is a values dictionary present in the data
        """
        data = {
            "action": "SIM"
        }
        serializer = ProtocolSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_invalid_action(self):
        """
        Test whether an invalid action is rejected
        """
        data = {
            "action": "INVALID",
            "values": {

            }
        }
        serializer = ProtocolSerializer(data=data)

        self.assertFalse(serializer.is_valid())
