import numpy as np
import pickle

from mido import MidiTrack, MidiFile

from project.algorithms.core.midi_segment import MidiSegment


class PitchVectorSegment(MidiSegment):

    def __init__(self, file: MidiFile, melody_track_ind: int, pitch_vector: np.ndarray, pitch_modifier: float,
                 start_offset: float):
        """
        A segment of a MIDI file represent as a multidimensional vector. Each component of the vector is an
        observation of what the pitch was at a particular point in time


        Args:
            file: The file the pitch vector was extracted from
            melody_track_ind: The specific MIDI track the vector was extracted from
            pitch_vector: The vector itself, normalized to have 0 mean
            pitch_modifier: A value, which when added to pitch_vector, produces the original vector
            start_offset: The time (in seconds) at which this vector was extracted
        """
        super().__init__(file, melody_track_ind)
        self.pitch_vector = pitch_vector
        self.pitch_modifier = pitch_modifier
        self.start_offset = start_offset

    def save_segment(self, filepath: str):
        """
        Save the segment as a python ``pickle`` file.

        Args:
            filepath: The place to save the file to

        """
        with open(filepath, 'wb') as fh:
            pickle.dump(self, fh)

    def get_non_normalized_arr(self) -> np.ndarray:
        """
        Get back the original pitch vector without any normalization.

        Returns:
            The numpy array representing the pitch vector, with no normalization applied.
        """
        return self.pitch_vector + self.pitch_modifier

    def __str__(self):
        return f"pitch_modifier = {self.pitch_modifier} start_offset = {self.start_offset}\n" \
               f"pv = {str(self.pitch_vector)}"

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.pitch_vector)
