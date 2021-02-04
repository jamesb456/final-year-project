import numpy as np

from project.segment.segment import Segment


def reduce_segment(segment: Segment, window_size: int = -1) -> Segment:
    reduced_notes = np.array(segment.notes)  # create copy of note timeline

    return Segment(segment.track, reduced_notes)
