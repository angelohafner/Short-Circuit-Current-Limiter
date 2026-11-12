"""Captions must describe native electrical state, including the reclose step."""
import unittest
import scenes
from data_access import Measurements


class RecoveryCaptionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = Measurements()

    def caption(self, time):
        self.assertTrue(hasattr(scenes, 'recovery_caption'),
                        'Recovery captions must be derived from the current native state')
        return scenes.recovery_caption(self.data, time)

    def test_initial_state(self):
        self.assertEqual(self.caption(.49), 'Steady operation')

    def test_gate_off_is_not_scr_off(self):
        self.assertEqual(self.caption(.70), 'Gates off; natural current decay')

    def test_last_extinction_precedes_ready(self):
        self.assertEqual(self.caption(.825), 'SCRs off; waiting for recovery')

    def test_command_is_not_physical_reclosure(self):
        self.assertEqual(self.caption(1.2), 'Reclosure commanded')
        self.assertEqual(self.caption(1.201), 'Reclosed: compensation settling')

    def test_final_state(self):
        self.assertEqual(self.caption(2.5), 'Normal operation restored')


if __name__ == '__main__':
    unittest.main()
