import unittest

import mido

import project.segment.lbdm as lbdm


class LbdmTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mid_file = mido.MidiFile("../mid/test_midi_3.mid")
        self.test_track = self.mid_file.tracks[0]
        self.emp_track = mido.MidiTrack()
        self.one_note_track = mido.MidiTrack()
        self.one_note_track.append(mido.Message("note_on", note=60, velocity=127, time=0))

    def test_returns_normalized_intervals(self):
        lbdm_profile, sequence_profile = lbdm.lbdm(self.test_track)

        for arr in sequence_profile:
            for elem in arr:
                self.assertTrue(0.0 <= elem <= 1.0,
                                "Normalised interval value in sequence profile not between 0.0 and 1.0.")

        for elem in lbdm_profile:
            self.assertTrue(0.0 <= elem <= 1.0,
                            "Normalised interval value in lbdm profile not between 0.0 and 1.0.")

    def test_empty_track_returns_empty_arrays(self):
        lbdm_profile, sequence_profile = lbdm.lbdm(self.emp_track)
        self.assertTrue(len(lbdm_profile) == 0, f"Contents of lbdm profile for empty track are {lbdm_profile}, "
                                                f"expected []")
        for arr in sequence_profile:
            self.assertTrue(len(arr) == 0)

    def test_one_note_track_returns_empty_arrays(self):
        lbdm_profile, sequence_profile = lbdm.lbdm(self.emp_track)
        self.assertTrue(len(lbdm_profile) == 0, f"Contents of lbdm profile for one note track are {lbdm_profile},"
                                                f" expected []")
        for arr in sequence_profile:
            self.assertTrue(len(arr) == 0)


if __name__ == '__main__':
    unittest.main()
