from django.test import TestCase

from connections.consumers import *


class SimulationTestCase(TestCase):
    """

    """
    message_correct = None
    message_incorrect = None

    def setUp(self):
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
                                                     'title': 'GoToPos',
                                                     'id': '05d86396-986a-42bd-b1b9-5c47e1d94e62'}},
            'root': '05d86396-986a-42bd-b1b9-5c47e1d94e62'}},
            'type': 'simulate',
            'channel_name': 'specific.ONGYcQVC!RIeWJnGgWjUC'}

    def test_edit_tree(self):
        print("\n Testing incorrect tree...")
        completed_process = edit_tree(self.message_incorrect['values'])
        self.assertNotEqual(completed_process.returncode, 0)

        print("\n Testing correct tree...")
        completed_process = edit_tree(self.message_correct['values'])
        self.assertEqual(completed_process.returncode, 0)

    def test_simulation(self):
        print("\n Testing simulation of correct tree...")
        print("Starting ros and grsim")
        ros = start_ros()
        gr_sim = start_grsim()

        print("Starting tactic")
        completed_process = start_tactic()
        self.assertEqual(completed_process.returncode, 0)

        print("Tactic finished, closing grsim and ros")
        os.killpg(os.getpgid(gr_sim.pid), signal.SIGTERM)
        os.killpg(os.getpgid(ros.pid), signal.SIGTERM)
