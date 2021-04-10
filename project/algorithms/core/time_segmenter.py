from typing import List

from mido import MidiFile

from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.segmenter import Segmenter


class TimeSegmenter(Segmenter):
    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[MidiSegment]:
        pass