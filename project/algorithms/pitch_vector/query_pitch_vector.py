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

    print("Compare the query segment with the these vectors")

    for (window_size, observations), engine in vector_map.items():

        # segment the query song

        segmenter = PitchVectorSegmenter(window_size, observations)  # use window size and observations specific to
                                                                     # these mids
        query_segments = segmenter.create_segments(query_mid, melody_track)  # TODO: change to use arbitrary track index
        # TODO: this needs to change! songs not necessarily in the same tempo
        # TODO: see in paper about window size modifiers
        similarity_map = {}
        for query_segment in query_segments:
            neighbours = engine.neighbours(query_segment.pitch_vector)
            print(neighbours)

        sorted_dict = {k: v for k, v in sorted(similarity_map.items(), key=lambda item: item[1], reverse=True)}
        series = pd.Series(sorted_dict)
        series.to_csv(f"query_output/rankings/test.csv")
        for index, (mid_name, similarity) in enumerate(sorted_dict.items()):
            print(f"\t[{len(similarity_map.items()) - index}] {mid_name}: {similarity}")

        return sorted_dict
