import unittest
import pathlib
from mido import MidiTrack, MidiFile


from project.core.lbdm_segmenter import LbdmSegmenter
from project.visualisation.graph import pitch_time_graph, lbdm_graph

# test for structure:

# general procedure

# 1.) core each voice / track
# 2.) reduce each core
# 3.) make links between segments
# 4.) repeat steps 2-3 until each core contains one note


class GraphAlgorithmTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mid_file = MidiFile("../../mid/ashover13.mid")
        self.segmenter = LbdmSegmenter(threshold=0.5)

    def test_graph_algorithm_procedure(self):
        pass








