import pathlib
from functools import partial
from typing import List, Optional
from multiprocessing.pool import Pool

import numpy as np
from mido import MidiFile

from tqdm import tqdm

from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.midtools import is_monophonic
from project.algorithms.core.note_segment import NoteSegment
from project.algorithms.core.segmenter import Segmenter
from project.algorithms.query_creation.query_creator import QueryCreator


class IndexedQueryCreator(QueryCreator):
    def __init__(self, segmenter: Segmenter, seed: Optional[int]):
        """
        A ``QueryCreator`` that creates queries based on the output of a segmentation function, represented by the
        ``Segmenter`` class.

        Args:
            segmenter: A Segmenter which is used to create the segments.
            seed: Seed for the random set of queries chosen after creating the segments
        """
        super().__init__()
        self.segmenter = segmenter
        self.seed = seed

    def create_queries(self, mid_folder: str, num_queries: int, melody_track: int, **segmenter_args) -> List[NoteSegment]:
        """
        Create query ``NoteSegments`` based on this classes designated `Segmenter`` object
        Args:
            mid_folder: A path to the folder containing the MIDI files to create segments from
            num_queries: The max number of query MIDI files to generate.
            melody_track: The track of on which the segmentation should be based
            segmenter_args: Any extra arguments for the chosen segmenter

        Returns:
            A list of up to num_queries segments that can be used as queries in the query_client or query_file scripts
        """
        if self.seed is not None:
            rng = np.random.default_rng(int(self.seed))
        else:
            rng = np.random.default_rng()
        mid_location = pathlib.Path(mid_folder)
        print("Loading MIDI files")

        # get all midi files
        all_mids = list(map(lambda path: MidiFile(path), mid_location.glob("*.mid")))
        print(f"{len(all_mids)} MIDI files found")
        # remove any polyphonic files
        available_mids = list(filter(lambda file: is_monophonic(file.tracks[melody_track]), all_mids))
        print(f"{len(all_mids) - len(available_mids)} polyphonic MIDIs ignored. Total is now {len(available_mids)}")

        # create segments, then sample from them
        segments = []
        for mid in tqdm(available_mids, desc="Segmenting MIDI files"):
            segments.extend(self.segmenter.create_segments(mid, melody_track, **segmenter_args))

        total_length = len(segments)
        print(f"Created {total_length} segments.")
        # remove small segments
        segments = [segment for segment in segments if len(segment) >= 4]
        print(f"Removed {total_length - len(segments)} small segments of less than 4 notes")
        return list(rng.choice(segments, num_queries, replace=False))
