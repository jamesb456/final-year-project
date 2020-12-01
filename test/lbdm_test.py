import unittest

import mido

import project.segment.lbdm as lbdm


class LbdmTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mid_file = mido.MidiFile("../mid/test_midi_3.mid")
        self.test_track = self.mid_file.tracks[0]

    def test_returns_valid_intervals(self):
        _, s_profile = lbdm.lbdm(self.test_track)
        for arr in s_profile:
            for elem in arr:
                self.assertTrue(0.0 <= elem <= 1.0, "Normalised interval value not between 0.0 and 1.0.")


if __name__ == '__main__':
    unittest.main()
