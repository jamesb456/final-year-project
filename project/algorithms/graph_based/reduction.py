import numpy as np

from project.segment.segment import Segment


def reduce_segment(segment: Segment, window_size: int = -1) -> Segment:
    reduced_notes = []

    # work out the window size
    if window_size == -1:
        # find the shortest note
        # duration of note = end - start
        shortest_note_length = segment.find_shortest_note_length()

        window_size = shortest_note_length * 2

    

    return Segment(segment.file, reduced_notes)
