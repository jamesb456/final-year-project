import unittest

import mido

from project.segment import lbdm
from project.algorithms.graph_based import reduction

# 1: segment via lbdm
# 2: "reduce" each segment by removing the least "relevant" notes
# 3: identify connections between sections: if segment s0 reduces to s1 then create a connection
# (also could identify other transformations such as inversion and transposition between different keys)
# 4: repeat step 2-3 until all segments have only one note


class GraphAlgorithmTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mid_file = mido.MidiFile("../../mid/test_midi_3.mid")
        self.test_track = self.mid_file.tracks[0]
        self.threshold = 0.5

    def test_graph_algorithm_procedure(self):
        boundary_profile, _ = lbdm.lbdm(self.test_track, pitch_weight=0.33, ioi_weight=0.67, rest_weight=0)
        # ordinarily: segment based on lbdm results but here just reuse whole track

        new_track = reduction.reduce(self.test_track, (4, 4), 0, self.mid_file.ticks_per_beat)
