from typing import Optional


class Note:
    """
    Represents a note found within a MIDI file. It's convenient to have a class to represents the notes because
    notes within MIDI files are represented as messages telling a MIDI device whether a note is being pressed down or
    not. Therefore, you get 2 messages per note: one for "onset" point of notes (when for example a piano note should
    start being played) and one for the "offset" point (when the note should stop playing / fade out depending on what's
    playing the music)

    """
    def __init__(self, start: int, end: int, pitch: int, chord: Optional[int] = None,
                 start_message_index: Optional[int] = None, end_message_index: Optional[int] = None):
        self.start_time = start
        self.end_time = end
        self.pitch = pitch
        self.chord = chord
        self.start_message_index = start_message_index
        self.end_message_index = end_message_index

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time
