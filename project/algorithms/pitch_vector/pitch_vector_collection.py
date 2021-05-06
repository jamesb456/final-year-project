from typing import List

from mido import MidiFile
from project.algorithms.pitch_vector.pitch_vector_segment import PitchVectorSegment


class PitchVectorCollection:
    def __init__(self, mid_file: MidiFile, vectors: List[PitchVectorSegment], window_size: float, observations: int,
                 melody_track: int):
        """
        A collection of pitch vectors. Use to serialize the pitch vectors for each song to disk.

        Args:
            mid_file: The MIDI file the pitch vectors were created from
            vectors: The pitch vectors themselves, produced from pitch_vector_segmenter
            window_size: The window size used when segmenting
            observations: The number of dimensions per pitch vector
            melody_track: The MidiTrack from which pitch vectors were extracted from
        """

        self.vectors = vectors
        self.mid_file = mid_file
        self.window_size = window_size
        self.observations = observations
        self.melody_track = melody_track


