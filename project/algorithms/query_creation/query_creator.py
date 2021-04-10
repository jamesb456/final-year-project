from abc import ABC, abstractmethod
from typing import List

from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.note_segment import NoteSegment


class QueryCreator(ABC):

    def __init__(self):
        """
        An abstract class to create a list of "query" midi files to be used to test QBE algorithms
        """
        pass

    @abstractmethod
    def create_queries(self, mid_folder: str, num_queries: int, melody_track: int, n_processes: int = 3) \
            -> List[NoteSegment]:
        """
        Create a list of query ``NoteSegment``  from the given MIDI files using some strategy.

        Args:
            mid_folder: A path to the folder containing the MIDI files to create segments from
            num_queries: The max number of query MIDI files to generate.
            melody_track: The track of on which the segmentation should be based
            n_processes: The number of processes used to create the query segments

        Returns:
            A list of up to `num_queries` segments that can be used as queries in the query_client or query_file scripts
        """
        pass
