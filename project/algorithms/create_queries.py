import pathlib
import sys
from typing import Optional, List

import numpy as np

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
                            melody_track: int, rng: Optional[int],
                            transpose: int = 0, note_duration_transform: float = 1, extra_notes: int = 0,
                            removed_notes: int = 0, modified_notes: int = 0, **kwargs) -> List[NoteSegment]:
    indexed_queries = create_indexed_queries(algorithm, num_queries, dataset_location, melody_track, rng, **kwargs)

    if rng is not None:
        rand = np.random.default_rng(int(rng))
    else:
        rand = np.random.default_rng()

    for query in indexed_queries:

        for i in range(removed_notes):
            pass
        for j in range(extra_notes):
            pass
        query.elongate_notes(note_duration_transform)
        query.transpose(transpose)
        for k in range(modified_notes):
            pass

    return indexed_queries


def create_random_queries(num_queries: int, dataset_location: str,
                          melody_track: int, **kwargs) -> List[NoteSegment]:
    pass
