from math import floor
from typing import Optional, Tuple

import project.util.constants as constants
from project.segment.chord import Chord
from project.segment.signature import TimeSignature, KeySignature


class Note:
    """
    Represents a note found within a MIDI file. It's convenient to have a class to represents the notes because
    notes within MIDI files are represented as messages telling a MIDI device whether a note is being pressed down or
    not. Therefore, you get 2 messages per note: one for "onset" point of notes (when for example a piano note should
    start being played) and one for the "offset" point (when the note should stop playing / fade out depending on what's
    playing the music)

    """

    def __init__(self, start: int, end: int, pitch: int, channel: int = 0, chord: Optional[Chord] = None,
                 start_message_index: Optional[int] = None, end_message_index: Optional[int] = None):
        self.start_time = start
        self.end_time = end
        self.pitch = pitch
        self.channel = channel
        self.chord = chord
        self.start_message_index = start_message_index
        self.end_message_index = end_message_index

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time

    def get_metric_strength(self, ticks_per_beat: int, time_signature: TimeSignature,
                            time_since_time_sig: int) -> float:
        ticks_since_time_signature = self.start_time - time_since_time_sig
        bar_length = (ticks_per_beat * (time_signature.numerator * (4 / time_signature.denominator)))
        # approx beat (zero index) is the time from last signature change to current note, modulo the length
        # of one full bar. This gives the number of ticks you are through the current bar/measure. Now scale
        # in terms of beat and restrain from 0 to 3
        # round to nearest beat. if this would round to too high an index, consider it part of the next beat
        beat_index = \
            round((ticks_since_time_signature % bar_length) / ticks_per_beat) % time_signature.numerator

        beat_strength = 0
        if (time_signature.numerator, time_signature.denominator) in constants.BEAT_STRENGTH_DICT.keys():
            beat_strength = constants.BEAT_STRENGTH_DICT[(time_signature.numerator, time_signature.denominator)][beat_index]
        else:
            if beat_index == 1:
                beat_strength = 0.4
            else:
                beat_strength = 0.1

        return beat_strength

    def get_consonance_score(self):
        # get the difference between this note's pitch and it's underlying chord
        if self.chord is None:
            return 0.5
        else:
            note_tone = self.pitch % constants.OCTAVE_SEMITONE_COUNT
            interval = abs(self.chord.root_tone - note_tone)
            return constants.CONSONANCE_SCORE_DICT[interval]

    def str(self):
        return self.__str__()

    def repr(self):
        return self.__repr__()

    def __str__(self):

        if self.pitch < 0 or self.pitch > 127:
            scientific_note = str(self.pitch) + " (out of range)"
        else:
            scientific_note = constants.TWELVE_NOTE_SCALE[self.pitch % 12] + str(floor((self.pitch - 12) / 12.0))

        base = f"Note {scientific_note} start={self.start_time} length={self.duration} " \
               f"channel={self.channel}"
        if self.chord is not None:
            base += f"chord={self.chord}"
        return base

    def __repr__(self):
        return self.__str__()

    def get_functional_score(self, key_signature: KeySignature):
        if self.chord is None:  # if there is no chord associated with this note, return an average strength
            return 0.5
        else:
            functional_score = constants.FUNCTIONAL_SCORE_DICT[abs(key_signature.note - self.chord.root_tone)]
            return functional_score
