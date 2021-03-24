import time
from collections import defaultdict, OrderedDict

import json
import numpy as np
import pandas as pd

from typing import Dict, Tuple
from mido import MidiFile, tick2second
from nearpy import Engine

from project.algorithms.pitch_vector.pitch_vector_segmenter import PitchVectorSegmenter
from project.algorithms.pitch_vector.vector_candidate import VectorCandidate
from project.algorithms.core.midtools import get_start_offset, get_end_offset


def query_pitch_vector(midi_path: str, vector_map: Dict[Tuple[float, int], Engine],
                       melody_track: int = 0) -> Dict[str, float]:
    # build up database of pitch vectors
    # then segment the query based on the different window sizes and observations
    # in the database

    query_mid = MidiFile(midi_path)
    query_start, start_index = get_start_offset(query_mid.tracks[melody_track], query_mid.ticks_per_beat)
    query_end, end_index = get_end_offset(query_mid.tracks[melody_track], query_mid.ticks_per_beat)

    print("Compare the query segment with the database of vectors")

    similarity_map = defaultdict(lambda: 0)

    for (window_size, observations), engine in vector_map.items():
        candidates = []
        # segment the query song
        # using different window times
        window_modifiers = np.linspace(0.65, 1.7, 17)  # arguments taken from the paper
        print("Extract several pitch vectors with different modifiers for the window size")
        print("(the query may be faster/slower then the actual part of the song)")

        for modifier in window_modifiers:
            segmenter = PitchVectorSegmenter(window_size * modifier, observations)
            query_segments = segmenter.create_segments(query_mid, melody_track)
            for query_segment in query_segments:
                neighbours = engine.neighbours(query_segment.pitch_vector)
                for vec, (mid_name, cand_offset, pitch_mod), distance in neighbours:
                    candidates.append(VectorCandidate(query_segment.start_offset, modifier, cand_offset,
                                                      mid_name))

        print(f"Number of candidates is {len(candidates)}")

        for candidate in candidates:
            print(f"{candidate} approx bounds = {candidate.get_candidate_segment_bounds(query_start, query_end)}")
        # curr_time = time.strftime("%Y%m%d_%I%M%S")
        # with open(f"{curr_time}_candidates.json", "w") as fh:
        #     json.dump(list(map(lambda c: c.__dict__, candidates)), fh)

    sorted_dict = {k: v for k, v in sorted(similarity_map.items(), key=lambda item: item[1])}
    series = pd.Series(sorted_dict)
    series.to_csv(f"query_output/rankings/test.csv")
    for index, (mid_name, similarity) in enumerate(sorted_dict.items()):
        print(f"\t[{len(similarity_map.items()) - index}] {mid_name}: {similarity}")

    return sorted_dict
