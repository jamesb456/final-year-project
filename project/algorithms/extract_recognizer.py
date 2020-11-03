from abc import ABC, abstractmethod
from mido import MidiFile
from typing import List, Dict


class ExtractRecognizer(ABC):
    @abstractmethod
    def recognize(self, extract: MidiFile, candidates: List[MidiFile]) -> List[float]:
        """
        Determines whether a given song extract is from a list of possible candidates. Returns a list of floating
        point values denoting the probability that the extract is part of the MIDI file at that index
        Args:
            extract: A MIDI object representing a possible extract from one of the candidates
            candidates: A list of MIDI files that the extract could have come from

        Returns:
              a list of floating point values denoting the probability that the extract is part of the MIDI file at
              that index in the list candidates
        """
        pass


