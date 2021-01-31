from abc import ABC, abstractmethod
from typing import List

from mido import MidiFile

from project.segment.segment import Segment


class Segmenter(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def create_segments(self, mid: MidiFile) -> List[Segment]:
        pass
