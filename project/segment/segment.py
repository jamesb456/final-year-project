from mido import MidiTrack

import project


class Segment:
    def __init__(self, track: MidiTrack, start_index: int, end_index: int):
        self.track = track  # source track
        self.start_index = start_index  # index of the first MIDI message of the segment (in the source track)
        self.end_index = end_index  # index of the last MIDI message of the segment (in the source track)

    def create_reduction(self, window_size: int):
        # create
        pass

    def get_notes(self):
        return self.track[self.start_index:self.end_index]

