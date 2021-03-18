import numpy as np

from typing import Optional

from mido import MidiTrack, MidiFile

from project.core.segment.midi_segment import MidiSegment


class PitchVectorSegment(MidiSegment):

    def __init__(self, file: MidiFile, melody_track_ind: int, pitch_vector: np.ndarray, window_size: float,
                 observations: int, pitch_modifier: float, start_offset: float):
        super().__init__(file, melody_track_ind)
        self.pitch_vector = pitch_vector
        self.window_size = window_size
        self.observations = observations
        self.pitch_modifier = pitch_modifier
        self.start_offset = start_offset

    def copy_notes_to_track(self, track: MidiTrack):
        pass

    def save_segment(self, filepath):
        pass

    def save_as_midi(self, filepath):
        pass

    def __repr__(self):
        return f"window_size = {self.window_size} observations = {self.observations} " \
               f"pitch_modifier = {self.pitch_modifier} start_offset = {self.start_offset}\n" \
               f"pv = {str(self.pitch_vector)}"
