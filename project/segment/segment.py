import numpy as np
from mido import MidiFile

import project


class Segment:
    def __init__(self, file: MidiFile, notes: np.ndarray):
        self.track = file  # source track
        self.notes = notes

    def __len__(self):
        return len(self.notes)
