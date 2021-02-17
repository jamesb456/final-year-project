import unittest
import pathlib
from mido import MidiTrack, MidiFile


from project.segment.lbdm_segmenter import LbdmSegmenter
from project.visualisation.graph import pitch_time_graph, lbdm_graph

# test for structure:

# general procedure

# 1.) segment each voice / track
# 2.) reduce each segment
# 3.) make links between segments
# 4.) repeat steps 2-3 until each segment contains one note


class GraphAlgorithmTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mid_file = MidiFile("../../mid/ashover13.mid")
        self.segmenter = LbdmSegmenter(threshold=0.5)

    def test_graph_algorithm_procedure(self):
        sigs = get_track_time_signatures(self.mid_file.tracks[0])

        mid_name = pathlib.Path(self.mid_file.filename).stem
        print(f"Segmenting {mid_name}.mid")
        segments = self.segmenter.create_segments(self.mid_file, 0)
        print("Done Segmentation")

        mid_location = f"../../mid/generated/{mid_name}"
        pathlib.Path(mid_location).mkdir(parents=True, exist_ok=True)
        print("Saving original segments to {}...".format(pathlib.Path(mid_location).resolve()))

        for (index, segment) in enumerate(segments):
            segment.save_segment(f"{mid_location}/segment_{index}.mid")

        print("Attempting first reduction")
        reduced_segments = list(map(lambda seg: reduce_segment(seg), segments))

        print("Attempting second reduction")
        double_reduced_segments = list(map(lambda seg: reduce_segment(seg), reduced_segments))

        print("Attempting third reduction")
        triple_reduced_segments = list(map(lambda seg: reduce_segment(seg), double_reduced_segments))

        print("Saving reduced segments to {}...".format(pathlib.Path(mid_location).resolve()))
        for (index, reduced_segment) in enumerate(reduced_segments):
            reduced_segment.save_segment(f"{mid_location}/reduced_segment_{index}.mid")

        for (index, reduced_segment) in enumerate(double_reduced_segments):
            reduced_segment.save_segment(f"{mid_location}/double_reduced_segment_{index}.mid")

        for (index, reduced_segment) in enumerate(triple_reduced_segments):
            reduced_segment.save_segment(f"{mid_location}/triple_reduced_segment_{index}.mid")









