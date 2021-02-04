import unittest

from mido import MidiTrack, MidiFile

from project.segment.lbdm_segmenter import LbdmSegmenter

# test for structure:

# general procedure

# 1.) segment each voice / track
# 2.) reduce each segment
# 3.) make links between segments
# 4.) repeat steps 2-3 until each segment contains one note


class GraphAlgorithmTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mid_file = MidiFile("../../mid/busy_schedule_sax.mid")
        self.segmenter = LbdmSegmenter()

    def test_graph_algorithm_procedure(self):
        segments = self.segmenter.create_segments(self.mid_file)
        







