from abc import ABC, abstractmethod
from typing import List

from mido import MidiFile

from project.core.graph_segment import GraphSegment
from project.core.midi_segment import MidiSegment


class Segmenter(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[MidiSegment]:
        pass

