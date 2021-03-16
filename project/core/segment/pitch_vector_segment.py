import numpy as np

from typing import Optional

from mido import MidiTrack, MidiFile

from project.core.segment.midi_segment import MidiSegment


class PitchVectorSegment(MidiSegment):

    def __init__(self, file: MidiFile, melody_track_ind: int, pitch_vector: np.ndarray, window_size: float,
                 observations: int, pitch_modifier: int):
        super().__init__(file, melody_track_ind)
        self.pitch_vector = pitch_vector
        self.window_size = window_size
        self.observations = observations
        self.pitch_modifier = pitch_modifier

    @property
    def start_time(self) -> Optional[int]:
        return 0

    @property
    def end_time(self) -> Optional[int]:
        return 0

    def copy_notes_to_track(self, track: MidiTrack):
        pass

    def save_segment(self, filepath):
        pass
