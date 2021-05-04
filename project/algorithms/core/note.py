import sys
from math import floor
from typing import Optional

import project.algorithms.core.constants as constants
from project.algorithms.core.chord import Chord
from project.algorithms.graph_based.signature import TimeSignature, KeySignature


class Note:
    def __init__(self, start: float, end: float, pitch: float, channel: int = 0, chord: Optional[Chord] = None,
                 start_message_index: Optional[int] = None, end_message_index: Optional[int] = None):
        """
        Represents a note found within a MIDI file. It's convenient to have a class to represents the notes because
        notes within MIDI files are represented as messages telling a MIDI device whether a note is being pressed down or
        not. Therefore, you get 2 messages per note: one for "onset" point of notes (when for example a piano note should
        start being played) and one for the "offset" point (when the note should stop playing / fade out depending on what's
        playing the music)

        Args:
            start: the start of the note; either as ticks, or a normalized value
            end: the end of the note; either as ticks, or a normalized value
            pitch: the pitch (either a MIDI note number, or a normalized value) of the notes
            channel: the MIDI channel this note is played on (only used for saving MIDI notes)
            chord: the underlying chord of this note (default is None as there may be no underlying chords)
            start_message_index: the index in a MIDI track of the note_on event this Note is derived from (default is None as there may be no corresponding MidiTrack)
            end_message_index: the index in a MIDI track of the note_off event this Note is derived from (default is None as there may be no corresponding MidiTrack)
        """
        self.start_time = start
        self.end_time = end
        self.pitch = pitch
        self.channel = channel
        self.chord = chord
        self.start_message_index = start_message_index
        self.end_message_index = end_message_index

    @property
    def duration(self) -> float:
        """
        Return the duration of the note

        Returns:
            the duration of the note
        """
        return self.end_time - self.start_time

    def get_metric_strength(self, ticks_per_beat: int, time_signature: TimeSignature,
                            time_since_time_sig: int) -> float:
        """
        Get the metrical strength of this note, given where it is in the music.
        This method finds which position this note is in within a bar, and then finds the metrical strength
        based on the time signature.

        Args:
            ticks_per_beat: The ticks_per_beat of the MIDI file this note is contained within
            time_signature: The time signature
            time_since_time_sig: The time since the time signature last changed.

        Returns:
            A number between 0 and 1.0 representing the relative metrical strength of this note
        """
        ticks_since_time_signature = self.start_time - time_since_time_sig
        bar_length = (ticks_per_beat * (time_signature.numerator * (4 / time_signature.denominator)))
        # approx beat (zero index) is the time from last signature change to current note, modulo the length
        # of one full bar. This gives the number of ticks you are through the current bar/measure. Now scale
        # in terms of beat and restrain from 0 to 3
        # round to nearest beat. if this would round to too high an index, consider it part of the next beat
        beat_index = round((ticks_since_time_signature % bar_length) / ticks_per_beat) % time_signature.numerator

        beat_strength = 0
        if (time_signature.numerator, time_signature.denominator) in constants.BEAT_STRENGTH_DICT.keys():
            beat_strength = constants.BEAT_STRENGTH_DICT[(time_signature.numerator, time_signature.denominator)][
                beat_index]
        else:
            sys.stderr.write(f"Time signature {time_signature.__repr__()} not in beat strength dict\n")
            sys.stderr.flush()
            if beat_index == 1:
                beat_strength = 0.4
            else:
                beat_strength = 0.1

        return beat_strength

    def get_consonance_score(self):
        """
            Return the consonance score of this note, dependent on the interval between this note's pitch and
            its underlying chord (if one exists)

        Returns:
            A score representing the consonance between this note's pitch and its underlying chord. If there is no
            underlying chord, a default value of 0.5 is returned
        """

        # get the difference between this note's pitch and it's underlying chord
        if self.chord is None:
            return 0.5
        else:
            interval = abs(
                (self.chord.root_tone % constants.OCTAVE_SEMITONE_COUNT) -
                (self.pitch % constants.OCTAVE_SEMITONE_COUNT)
            )
            return constants.CONSONANCE_SCORE_DICT[interval]

    def get_functional_score(self, key_signature: KeySignature):
        """
            Return the functional score of this note, dependent on the interval between the underlying chord and the
            given key signature. If this note doesn't have an underlying, a a default value of 0.5 is returned instead

            Args:
                key_signature: The key signature the functional score should be relative to
            Returns:
                 A functional score between this note's underlying chord and a given key signature If there is no
                 underlying chord, a default value of 0.5 is returned
            """
        if self.chord is None:  # if there is no chord associated with this note, return an average strength
            return 0.5
        else:
            return constants.FUNCTIONAL_SCORE_DICT[abs(key_signature.note -
                                                       (self.chord.root_tone % constants.OCTAVE_SEMITONE_COUNT))]

    def normalize(self, mean_pitch: float, start_offset: int, sequence_length: int) -> "Note":
        """
        Return a normalized version of this note based on:\n
        * A mean pitch value to be subtracted from this note's pitch
        * The start time of the sequence of notes (which this note is a part of) to be normalized
        * The number of notes in the aforementioned sequence of notes

        Args:
            mean_pitch: The mean pitch of the sequence of notes to be normalized
            start_offset: The start offset of the sequence of notes to be normalized
            sequence_length: The number of notes in the sequence to be normalized

        Returns:
            A new note normalized in all aspects with respect to the provided arguments
        """
        pitch = self.pitch - mean_pitch
        start_time = (self.start_time - start_offset) / sequence_length
        end_time = (self.end_time - start_offset) / sequence_length
        return Note(start_time, end_time, pitch, self.channel, self.chord, self.start_message_index,
                    self.end_message_index)

    def str(self):
        return self.__str__()

    def repr(self):
        return self.__repr__()

    def __str__(self):
        """
        Returns a textual representation of this note, meaning:\n
        the pitch (scientific pitch notation + MIDI value), start_time, duration, midi channel, and (if it exists) the
        underlying chord.

        Returns:
            A textual representation of the Note.
        """
        if self.pitch < constants.MIN_MIDI_VALUE or self.pitch > constants.MAX_MIDI_VALUE:
            scientific_note = str(self.pitch) + " (out of range)"
        else:
            scientific_note = constants.TWELVE_NOTE_SCALE_SHARP[int(self.pitch) % constants.OCTAVE_SEMITONE_COUNT] + \
                              str(floor((int(self.pitch) - constants.OCTAVE_SEMITONE_COUNT) / 12.0))

        base = f"Note {scientific_note} (MIDI note {self.pitch}) start={self.start_time} length={self.duration} " \
               f"channel={self.channel}"
        if self.chord is not None:
            base += f"chord={self.chord}"
        return base

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: "Note") -> bool:
        """
        Returns whether the two notes are equal. This is solely based on pitch and duration.

        Args:
            other: another note to compare with

        Returns:
            True if the two notes are the same, False otherwise.
        """
        return self.duration == other.duration and self.pitch == other.pitch
