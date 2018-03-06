from django.test import TestCase

from connections.serializers import *


class ProtocolSerializerTest(TestCase):

    def test_sim(self):
        data = {
            "action": "SIM",
            "values": {
                "tree": {

                }
            }
        }
        serializer = ProtocolSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["action"], "SIM")
        self.assertEqual(type(serializer.validated_data["values"]), dict)
        self.assertEqual(type(serializer.validated_data["values"]["tree"]),
                         dict)

    def test_stop(self):
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
        data = {
            "values": {

            }
        }
        serializer = ProtocolSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_values_presence(self):
        data = {
            "action": "SIM"
        }
        serializer = ProtocolSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_invalid_action(self):
        data = {
            "action": "INVALID",
            "values": {

            }
        }
        serializer = ProtocolSerializer(data=data)

        self.assertFalse(serializer.is_valid())
