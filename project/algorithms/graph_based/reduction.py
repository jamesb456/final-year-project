from typing import Tuple

import numpy as np

from project.segment.note import Note
from project.segment.segment import Segment


def round_to_nearest_beat(ticks: int, ticks_per_beat: int) -> int:
    min_resolution = ticks_per_beat / 8  # 32nd note / demi-semiquaver
    return int(round(ticks / min_resolution) * min_resolution)


def reduce_segment(segment: Segment, window_size: int = -1) -> Segment:
    reduced_notes = []

    # work out the window size
    if window_size == -1:
        # find the shortest note
        # duration of note = end - start
        shortest_note_length = segment.find_shortest_note_length()

        window_size = shortest_note_length * 2

    start_position = segment.start_time
    while start_position < segment.end_time:
        window_notes = segment.get_notes_in_time_range(start_position, window_size)

        if len(window_notes) == 0:
            start_position += window_size
        elif len(window_notes) == 1:
            # need to cover note if there's 1 though so the whole window is occupied
            # if the note extends beyond the window, keep it at that length
            # else extend to the length of the window (either forward or backward)
            end_of_window = start_position + window_size
            end_position = 0
            if window_notes[0].end_time > end_of_window:
                end_position = window_notes[0].end_time

            else:
                end_position = end_of_window

            new_note = Note(start_position, end_position, window_notes[0].pitch,
                            window_notes[0].channel, window_notes[0].chord)

            reduced_notes.append(new_note)
            start_position += new_note.duration

        else:  # choose the most relevant note

            # for TESTING use the first note always
            new_note = Note(start_position, window_notes[-1].end_time,
                            window_notes[0].pitch, window_notes[0].channel, window_notes[0].chord)
            # we don't care about start_message_index, end_message_index because it's no longer from a track
            reduced_notes.append(new_note)
            start_position += new_note.duration

    bad_notes = [(note1, note2) for (note1, note2) in zip(reduced_notes, reduced_notes[1:])
                 if note1.end_time > note2.start_time]
    assert bad_notes == [], f"Bad note pairs: {bad_notes}]"

    return Segment(segment.file, segment.melody_track_ind, reduced_notes)
