from abc import ABC, abstractmethod
from typing import List

from mido import MidiFile

from project.core.segment import Segment


class Segmenter(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[Segment]:
        pass

