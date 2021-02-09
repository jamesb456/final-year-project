from typing import Tuple

import numpy as np

from project.segment.note import Note
from project.segment.segment import Segment


def reduce_segment(segment: Segment, window_size: int = -1) -> Segment:
    reduced_notes = []

    # work out the window size
    if window_size == -1:
        # find the shortest note
        # duration of note = end - start
        shortest_note_length = segment.find_shortest_note_length()

        window_size = shortest_note_length * 2

    start_position = 0
    while start_position < segment.end_time:
        window_notes = segment.get_notes_in_time_range(start_position, window_size)
        if len(window_notes) < 2:  # if there's 0 or 1 notes in the window just add the notes to the new set of notes
            reduced_notes.extend(window_notes)
        else:  # choose the most relevant note
            # for TESTING use the first note always
            new_note = Note(window_notes[0].start_time, window_notes[-1].end_time,
                            window_notes[0].pitch, window_notes[0].chord)
            # we don't care about start_message_index, end_message_index because it's no longer from a track

        start_position += window_size

    return Segment(segment.file, segment.melody_track_ind, reduced_notes)
