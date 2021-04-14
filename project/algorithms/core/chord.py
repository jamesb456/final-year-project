from collections import defaultdict
from typing import List

import numpy as np

import project.algorithms.core.constants as constants
from enum import IntEnum, IntFlag


class Chord:

    def __init__(self, *notes: int):
        if len(notes) == 0:
            raise ValueError("A chord must have at least one note")
        self.root_tone = notes[0]
        self.norm_notes = np.array(notes) - self.root_tone

    def to_midi_values(self) -> List[int]:
        return list(self.norm_notes + self.root_tone)

    def __str__(self):
        return constants.TWELVE_NOTE_SCALE[self.root_tone % constants.OCTAVE_SEMITONE_COUNT]

    def __repr__(self):
        return self.__str__()
