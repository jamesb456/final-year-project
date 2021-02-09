from typing import List

from mido import MidiFile

from project.segment.note import Note


class Segment:
    def __init__(self, file: MidiFile, notes: List[Note]):
        self.file = file  # source track
        self.notes = notes

    def __len__(self):
        return len(self.notes)

    def find_shortest_note_length(self) -> int:
        return min([note.duration for note in self.notes])

