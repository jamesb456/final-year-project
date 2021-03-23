from collections import defaultdict

import numpy as np
import pandas as pd

from typing import Dict, Tuple
from mido import MidiFile
from nearpy import Engine

from project.algorithms.pitch_vector.pitch_vector_segmenter import PitchVectorSegmenter


def query_pitch_vector(midi_path: str, vector_map: Dict[Tuple[float, int], Engine],
                       melody_track: int = 0) -> Dict[str, float]:
    # build up database of pitch vectors
    # then segment the query based on the different window sizes and observations
    # in the database

    query_mid = MidiFile(midi_path)

    print("Compare the query segment with the database of vectors")
    similarity_map = defaultdict(lambda: 0)
    for (window_size, observations), engine in vector_map.items():
        candidates = []
        # segment the query song
        # using different window times
        window_modifiers = np.linspace(0.65, 1.7, 17)
        print("Extract several pitch vectors with different modifiers for the window size")
        print("(the query may be faster/slower then the actual part of the song)")

        for modifier in window_modifiers:
            print(f"Window modifier={modifier} modified window size = {window_size * modifier}")
            segmenter = PitchVectorSegmenter(window_size * modifier, observations)
            query_segments = segmenter.create_segments(query_mid, melody_track)
            for query_segment in query_segments:
                neighbours = engine.neighbours(query_segment.pitch_vector)
                for vec, (mid_name, start_offset, pitch_mod), distance in neighbours:
                    similarity_map[mid_name] += 1

    sorted_dict = {k: v for k, v in sorted(similarity_map.items(), key=lambda item: item[1])}
    series = pd.Series(sorted_dict)
    series.to_csv(f"query_output/rankings/test.csv")
    for index, (mid_name, similarity) in enumerate(sorted_dict.items()):
        print(f"\t[{len(similarity_map.items()) - index}] {mid_name}: {similarity}")

    return sorted_dict
