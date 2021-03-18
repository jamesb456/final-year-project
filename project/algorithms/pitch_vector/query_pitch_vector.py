import pathlib
import pickle


import numpy as np
import pandas as pd

from collections import defaultdict, OrderedDict

from mido import MidiFile

from project.algorithms.pitch_vector.pitch_vector_collection import PitchVectorCollection
from project.core.segment.pitch_vector_segmenter import PitchVectorSegmenter


def query_pitch_vector(midi_path: str):
    # build up database of pitch vectors
    # then segment the query based on the different window sizes and observations
    # in the database
    vector_map = defaultdict(list)
    query_mid = MidiFile(midi_path)
    available_mids = pathlib.Path("mid/generated/pitch_vector").glob("**/*.pickle")
    print("Building up database of pitch vector collections (representing each midi file)")
    num_vectors = 0
    for mid in available_mids:
        with open(mid, "rb") as fh:
            pv_collection: PitchVectorCollection = pickle.load(fh)
        num_vectors += len(pv_collection.vectors)
        vector_map[(pv_collection.window_size, pv_collection.observations)].append(pv_collection)
    print(f"Done: number of vectors in database is: {num_vectors}")
    print("now compare the query segment with the these vectors")

    for (window_size, observations), pv_collections in vector_map.items():

        # segment the query song

        segmenter = PitchVectorSegmenter(window_size, observations)  # use window size and observations specific to
                                                                     # these mids
        query_segments = segmenter.create_segments(query_mid, 0)  # TODO: change to use arbitrary track index
        # TODO: this needs to change! songs not necessarily in the same tempo
        # TODO: see in paper about window size modifiers
        similarity_map = {}
        for pv_collection in pv_collections:
            print(f"Checking vectors from {pv_collection.mid_file.filename}.")
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
        series.to_csv("query_output/rankings/test.csv")
        for index, (mid_name, similarity) in enumerate(sorted_dict.items()):
            print(f"\t[{len(similarity_map.items()) - index}] {mid_name}: {similarity}")

