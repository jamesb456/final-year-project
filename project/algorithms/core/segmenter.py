from abc import ABC, abstractmethod
from typing import List

from mido import MidiFile

from project.algorithms.core.midi_segment import MidiSegment


class Segmenter(ABC):

    def __init__(self):
        """
        The Segementer class represents an object which takes a MIDI file and returns a list of ``MidiSegments``.
        """
        pass

    @abstractmethod
    def create_segments(self, mid: MidiFile, track_index: int, **kwargs) -> List[MidiSegment]:
        """
        Creates a list of ``MidiSegments`` from the given MidiFile ``mid``.

        Args:
            mid: The MIDI file to segment
            track_index: The index of the track to segment with respect to
            **kwargs: Any extra arguments that may be needed

        Returns:
            A list of MidiSegment created by running some segmentation algorithm
        """
        pass

