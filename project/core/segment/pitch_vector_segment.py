import numpy as np
import pickle
from typing import Optional

from mido import MidiTrack, MidiFile

from project.core.segment.midi_segment import MidiSegment


class PitchVectorSegment(MidiSegment):

    def __init__(self, file: MidiFile, melody_track_ind: int, pitch_vector: np.ndarray, pitch_modifier: float, start_offset: float):
        super().__init__(file, melody_track_ind)
        self.pitch_vector = pitch_vector
        self.pitch_modifier = pitch_modifier
        self.start_offset = start_offset

    def copy_notes_to_track(self, track: MidiTrack):
        pass

    def save_segment(self, filepath: str):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    def save_as_midi(self, filepath: str):
        pass

    def get_non_normalized_arr(self) -> np.ndarray:
        return self.pitch_vector + self.pitch_modifier

    def __str__(self):
        return f"pitch_modifier = {self.pitch_modifier} start_offset = {self.start_offset}\n" \
               f"pv = {str(self.pitch_vector)}"

    def __repr__(self):
        return self.__str__()
