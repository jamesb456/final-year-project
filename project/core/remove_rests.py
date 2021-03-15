from typing import List
from project.core.note import Note


def remove_rests(notes: List[Note]):
    if len(notes) <= 1:
        return  # no rests to remove
    else:
        for i in range(len(notes) - 1):
            notes[i].end_time = notes[i+1].start_time

