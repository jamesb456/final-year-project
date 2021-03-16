from functools import reduce
from typing import List

from mido import MidiFile, MidiTrack, tempo2bpm


from project.core.segment.pitch_vector_segment import PitchVectorSegment
from project.core.segment.segmenter import Segmenter
from project.util.midtools import get_note_timeline


class PitchVectorSegmenter(Segmenter):
    def __init__(self, window_size: float, observations: int):
        self.window_size = window_size
        self.observations = observations
        super().__init__()

    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[PitchVectorSegment]:
        track: MidiTrack = mid.tracks[track_index]
        

        return []
