
class Note:
    def __init__(self, start: int, end: int, pitch: int, chord=None, start_message_index=None, end_message_index=None):
        self.start_time = start
        self.end_time = end
        self.pitch = pitch
        self.chord = chord
        self.start_message_index = start_message_index
        self.end_message_index = end_message_index

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time

