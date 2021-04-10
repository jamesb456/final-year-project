import pathlib
from functools import partial
from typing import List
from multiprocessing.pool import Pool

import numpy as np
from mido import MidiFile
from numpy.random import default_rng
from tqdm import tqdm

from project.algorithms.core.midi_segment import MidiSegment
from project.algorithms.core.note_segment import NoteSegment
from project.algorithms.core.segmenter import Segmenter
from project.algorithms.query_creation.query_creator import QueryCreator


class IndexedQueryCreator(QueryCreator):
    def __init__(self, segmenter: Segmenter):
        """
        A ``QueryCreator`` that creates queries based on the output of a segmentation function, represented by the
        ``Segmenter`` class.

        Args:
            segmenter: A Segmenter which is used to create the segments.
        """
        super().__init__()
        self.segmenter = segmenter

    def create_queries(self, mid_folder: str, num_queries: int, melody_track: int,
                       n_processes: int = 3) -> List[NoteSegment]:
        rng = default_rng()
        """
        Create query ``NoteSegments`` based on this classes designated `Segmenter`` object
        Args:
            mid_folder: A path to the folder containing the MIDI files to create segments from
            num_queries: The max number of query MIDI files to generate.
            melody_track: The track of on which the segmentation should be based
            n_processes: The number of processes used to create the query segments

        Returns:
            A list of up to num_queries segments that can be used as queries in the query_client or query_file scripts
        """
        mid_location = pathlib.Path(mid_folder)
        print("Loading MIDI files")
        available_mids = list(map(lambda path: MidiFile(path), mid_location.glob("*.mid")))
        print("MIDI files loaded.")
        # create segments, then sample from them
        segments = []
        for mid in tqdm(available_mids, desc="Segmenting all input MIDI"):
            segments.append(self.segmenter.create_segments(mid, melody_track))
        # with Pool(n_processes) as p:
        #     segmenter_func = partial(self.segmenter.create_segments, track_index=melody_track)
        #     segments = p.map(segmenter_func, available_mids)

        # this horrible line flattens the list of lists into one big list
        seg_list = [segment for segment_list in segments for segment in segment_list]
        return list(rng.choice(seg_list, num_queries, replace=False))
