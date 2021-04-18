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

    def transpose(self, pitch_change: int):

        self.root_tone += pitch_change
        if self.root_tone > constants.MAX_MIDI_VALUE:  # put root note back in bounds of MIDI notes
            while self.root_tone > constants.MAX_MIDI_VALUE:
                self.root_tone -= constants.OCTAVE_SEMITONE_COUNT
        elif self.root_tone < constants.MIN_MIDI_VALUE:  # same as above but in reverse for notes < 0
            while self.root_tone < constants.MIN_MIDI_VALUE:
                self.root_tone += constants.OCTAVE_SEMITONE_COUNT

        for note in self.norm_notes:  # check normalized notes as well
            if self.root_tone + note > constants.MAX_MIDI_VALUE:
                while self.root_tone + note > constants.MAX_MIDI_VALUE:
                    self.root_tone -= constants.OCTAVE_SEMITONE_COUNT

        for note in self.norm_notes:
            if self.root_tone + note < constants.MIN_MIDI_VALUE:
                while self.root_tone + note < constants.MIN_MIDI_VALUE:
                    self.root_tone += constants.OCTAVE_SEMITONE_COUNT

        # assert constants.MIN_MIDI_VALUE <= self.root_tone <= constants.MAX_MIDI_VALUE
        # for note in self.norm_notes:
        #     assert constants.MIN_MIDI_VALUE <= self.root_tone + note <= constants.MAX_MIDI_VALUE, f"Expected a note \
        #     pitch between {constants.MIN_MIDI_VALUE } and {constants.MAX_MIDI_VALUE }, not {self.root_tone + note}"

    def __str__(self):
        return constants.TWELVE_NOTE_SCALE_SHARP[self.root_tone % constants.OCTAVE_SEMITONE_COUNT]

    def __repr__(self):
        return self.__str__()
