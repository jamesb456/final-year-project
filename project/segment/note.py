from math import floor
from typing import Optional, Tuple


class Note:
    """
    Represents a note found within a MIDI file. It's convenient to have a class to represents the notes because
    notes within MIDI files are represented as messages telling a MIDI device whether a note is being pressed down or
    not. Therefore, you get 2 messages per note: one for "onset" point of notes (when for example a piano note should
    start being played) and one for the "offset" point (when the note should stop playing / fade out depending on what's
    playing the music)

    """
    def __init__(self, start: int, end: int, pitch: int, channel: int = 0, chord: Optional[int] = None,
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

    def str(self):
        return self.__str__()

    def repr(self):
        return self.__repr__()

    def __str__(self):
        scale = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        scientific_note = ""
        if self.pitch < 0 or self.pitch > 127:
            scientific_note = str(self.pitch)
        else:
            scientific_note = scale[self.pitch % 12] + str(floor((self.pitch - 12) / 12.0))

        base = f"Note {scientific_note} start={self.start_time} length={self.duration} " \
               f"channel={self.channel}"
        if self.chord is not None:
            base += f"chord={self.chord}"
        return base

    def __repr__(self):
        return self.__str__()
