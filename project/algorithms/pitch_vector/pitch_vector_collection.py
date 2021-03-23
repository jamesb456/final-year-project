from typing import List

from mido import MidiFile
from project.algorithms.pitch_vector.pitch_vector_segment import PitchVectorSegment


class PitchVectorCollection:
    def __init__(self, mid_file: MidiFile, vectors: List[PitchVectorSegment], window_size: float, observations: int):
        self.vectors = vectors
        self.mid_file = mid_file
        self.window_size = window_size
        self.observations = observations


