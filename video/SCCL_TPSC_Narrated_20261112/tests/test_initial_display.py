"""Regression: a paused first frame must already show its real electrical state."""
import unittest
from visuals import indicator, GREEN

class InitialDisplayTest(unittest.TestCase):
    def test_closed_feeder_is_green_before_first_animation(self):
        chip=indicator('Feeder closed',lambda:True,(0,0),GREEN)
        self.assertEqual(chip[0].get_fill_color().to_hex().upper(),GREEN.upper())

if __name__=='__main__':unittest.main()
