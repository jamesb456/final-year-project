import pathlib
import sys
from typing import Optional, List

from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.note_segment import NoteSegment
from project.algorithms.core.time_segmenter import TimeSegmenter
from project.algorithms.graph_based.lbdm_segmenter import LbdmSegmenter

from project.algorithms.query_creation.indexed_query_creator import IndexedQueryCreator


def create_indexed_queries(algorithm: str, num_queries: int, dataset_location: str,
                           melody_track: int, rng: Optional[int], **kwargs) -> List[NoteSegment]:
    if algorithm == "graph":
        creator = IndexedQueryCreator(LbdmSegmenter(), rng)
    elif algorithm == "pitch_vector":
        creator = IndexedQueryCreator(TimeSegmenter(kwargs["segmenter_args"]["time"]), rng)
    else:
        sys.stderr.write(f"Error: algorithm {algorithm} is unknown, so can't create segments for it.")
        sys.stderr.flush()
        return []
    return creator.create_queries(dataset_location, num_queries, melody_track, **kwargs["segmenter_args"])


def create_modified_queries(algorithm: str, num_queries: int, dataset_location: str,
                            melody_track: int, **kwargs) -> List[NoteSegment]:
    pass


def create_random_queries(num_queries: int, dataset_location: str,
                          melody_track: int, **kwargs) -> List[NoteSegment]:
    pass
