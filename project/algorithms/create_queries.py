import pathlib
import sys
from typing import Optional, List

import numpy as np

from project.algorithms.core import constants
from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.note import Note
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
                            removed_notes: int = 0, **kwargs) -> List[NoteSegment]:
    indexed_queries = create_indexed_queries(algorithm, num_queries, dataset_location, melody_track, rng, **kwargs)
    print("Done creating indexed segments. Now modifying them with:")
    print(f"\ttranspose={transpose}")
    print(f"\tduration transform={note_duration_transform}")
    print(f"\textra notes={extra_notes}")
    print(f"\tremoved notes={removed_notes}")
    if rng is not None:
        rand: np.random.Generator = np.random.default_rng(int(rng))
    else:
        rand: np.random.Generator = np.random.default_rng()

    for query in indexed_queries:
        # remove random notes (starting from the highest index to prevent any indices becoming invalid)
        if removed_notes > 0:
            removed_note_indices = np.sort(np.array(rand.integers(0, len(query), size=min(removed_notes, len(query)))))[::-1]
            for removed_note_index in removed_note_indices:
                query.remove_note(removed_note_index)

        # sample new notes from a normal distribution based on the original segments mean pitch
        # so the notes are "realistic"
        if extra_notes > 0:
            mean_pitch = int(query.get_mean_pitch())
            range_pitch = constants.OCTAVE_SEMITONE_COUNT // 2

            added_notes = rand.integers(max(0, mean_pitch - range_pitch), min(127, mean_pitch + range_pitch),
                                        extra_notes)
            added_notes_indices = rand.integers(0, len(query), extra_notes)
            added_notes_length = rand.integers(1, 3, extra_notes) * int(query.ticks_per_beat / 2)

            for j in range(extra_notes):
                query.add_note(int(added_notes[j]), int(added_notes_length[j]), added_notes_indices[j])

            print(query.notes)

        query.change_duration_transform(note_duration_transform)
        query.transpose(transpose)

    return indexed_queries


def create_random_queries(num_queries: int, dataset_location: str,
                          melody_track: int, **kwargs) -> List[NoteSegment]:
    pass
