import numpy as np
from mido import MidiTrack

import project


class Segment:
    def __init__(self, track: MidiTrack, notes: np.ndarray):
        self.track = track  # source track
        self.notes = notes

