from django.test import TestCase

from connections.consumers import *


class SimulationTestCase(TestCase):
    """
    Class testing the simulation of certain predefined trees
    """
    message_correct = None
    message_incorrect = None

    def setUp(self):
        """
        Initialise a correct and an incorrect tree within a message
        """
        self.message_correct = {'values': {'tree': {'nodes': {
            '05d86396-986a-42bd-b1b9-5c47e1d94e62': {'parameters': {},
                                                     'name': 'GoToPos',
                                                     'description': '',
                                                     'properties': {'xGoal': 1,
                                                                    'yGoal': 1},
                                                     'display': {'x': 288,
                                                                 'y': 0},
                                                     'title': 'GoToPos_A',
                                                     'id': '05d86396-986a-42bd-b1b9-5c47e1d94e62'}},
            'root': '05d86396-986a-42bd-b1b9-5c47e1d94e62'}},
            'type': 'simulate',
            'channel_name': 'specific.ONGYcQVC!RIeWJnGgWjUC'}
        self.message_incorrect = {'values': {'tree': {'nodes': {
            '05d86396-986a-42bd-b1b9-5c47e1d94e62': {'parameters': {},
                                                     'name': 'GoToPos',
                                                     'description': '',
                                                     'properties': {'xGoal': 1,
                                                                    'yGoal': 1},
                                                     'display': {'x': 288,
                                                                 'y': 0},
                                                     'title': 'GoToPos_A',
                                                     'id': '05d86396-986a-42bd-b1b9-5c47e1d94e62'}},
            }},
            'type': 'simulate',
            'channel_name': 'specific.ONGYcQVC!RIeWJnGgWjUC'}

    def test_edit_tree(self):
        """
        Testing the building of an incorrect and a correct tree
        """
        print("\n Testing incorrect tree...")
        completed_process = edit_tree(self.message_incorrect['values'])
        self.assertNotEqual(completed_process.returncode, 0)

        print("\n Testing correct tree...")
        completed_process = edit_tree(self.message_correct['values'])
        self.assertEqual(completed_process.returncode, 0)
