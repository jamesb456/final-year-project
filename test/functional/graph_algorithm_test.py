import unittest

from mido import MidiTrack, MidiFile

from project.algorithms.graph_based.reduction import reduce_segment
from project.segment.lbdm_segmenter import LbdmSegmenter

# test for structure:

# general procedure

# 1.) segment each voice / track
# 2.) reduce each segment
# 3.) make links between segments
# 4.) repeat steps 2-3 until each segment contains one note


class GraphAlgorithmTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mid_file = MidiFile("../../mid/ashover13.mid")
        self.segmenter = LbdmSegmenter()

    def test_graph_algorithm_procedure(self):
        segments = self.segmenter.create_segments(self.mid_file, 0)
        reduced_segments = list(map(lambda seg: reduce_segment(seg), segments))
        double_reduced_segments = list(map(lambda seg: reduce_segment(seg), reduced_segments))
        triple_reduced_segments = list(map(lambda seg: reduce_segment(seg), double_reduced_segments))
        for (index, segment) in enumerate(segments):
            segment.save_segment(f"../../mid/generated/segment_{index}.mid")

        for (index, reduced_segment) in enumerate(reduced_segments):
            reduced_segment.save_segment(f"../../mid/generated/reduced_segment_{index}.mid")

        for (index, reduced_segment) in enumerate(double_reduced_segments):
            reduced_segment.save_segment(f"../../mid/generated/doubled_reduced_segment_{index}.mid")

        for (index, reduced_segment) in enumerate(triple_reduced_segments):
            reduced_segment.save_segment(f"../../mid/generated/triple_reduced_segment_{index}.mid")

        







