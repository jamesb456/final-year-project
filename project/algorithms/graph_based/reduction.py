import numpy as np

from project.segment.segment import Segment


def reduce(segment: Segment, window_size: int) -> Segment:
    reduced_notes = np.array(segment.notes)  # create copy of note timeline
    # do the reduction
    return Segment(segment.track, reduced_notes)
