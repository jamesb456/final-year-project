import pathlib
import pickle


import numpy as np
import pandas as pd

from collections import defaultdict, OrderedDict
from typing import Dict, Tuple, List
from mido import MidiFile
from tqdm import tqdm

from project.algorithms.pitch_vector.pitch_vector_collection import PitchVectorCollection
from project.core.segment.pitch_vector_segmenter import PitchVectorSegmenter


def query_pitch_vector(midi_path: str, vector_map: Dict[Tuple[float, int], List[PitchVectorCollection]],
                       melody_track: int = 0) -> Dict[str, float]:
    # build up database of pitch vectors
    # then segment the query based on the different window sizes and observations
    # in the database

    query_mid = MidiFile(midi_path)

    print("Compare the query segment with the these vectors")

    for (window_size, observations), pv_collections in vector_map.items():

        # segment the query song

        segmenter = PitchVectorSegmenter(window_size, observations)  # use window size and observations specific to
                                                                     # these mids
        query_segments = segmenter.create_segments(query_mid, melody_track)  # TODO: change to use arbitrary track index
        # TODO: this needs to change! songs not necessarily in the same tempo
        # TODO: see in paper about window size modifiers
        similarity_map = {}
        prog_bar = tqdm(pv_collections, desc=f"Pitch Vector: {pathlib.Path(midi_path).stem} Progress")  # wrap iterable in progress bar
        for pv_collection in prog_bar:
            # print(f"Checking vectors from {pv_collection.mid_file.filename}.")
            prog_bar.set_postfix({"current_vectors": pathlib.Path(pv_collection.mid_file.filename).stem})
            for i, pv in enumerate(pv_collection.vectors):
                sim = 0
                for query_segment in query_segments:
                    similarity = np.linalg.norm(query_segment.pitch_vector - pv.pitch_vector)
                    sim += similarity
                sim /= len(query_segments)  # mean similarity for THIS pitch vector
                if pv_collection.mid_file.filename not in similarity_map:
                    similarity_map[pv_collection.mid_file.filename] = sim
                else:
                    similarity_map[pv_collection.mid_file.filename] \
                        = min(sim, similarity_map[pv_collection.mid_file.filename])

        sorted_dict = {k: v for k, v in sorted(similarity_map.items(), key=lambda item: item[1], reverse=True)}
        series = pd.Series(sorted_dict)
        series.to_csv(f"query_output/rankings/test.csv")
        for index, (mid_name, similarity) in enumerate(sorted_dict.items()):
            print(f"\t[{len(similarity_map.items()) - index}] {mid_name}: {similarity}")

        return sorted_dict
