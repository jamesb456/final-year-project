from mido import MidiTrack

import project


class Segment:
    def __init__(self, track: MidiTrack):
        self.track = track

    def create_reduction(self):
        s = Segment(MidiTrack())
        return s



