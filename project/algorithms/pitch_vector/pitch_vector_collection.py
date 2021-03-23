import pathlib
import pickle
from typing import List, Dict, Tuple

from mido import MidiFile
from tqdm import tqdm
from project.algorithms.pitch_vector.pitch_vector_segment import PitchVectorSegment
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections


class PitchVectorCollection:
    def __init__(self, mid_file: MidiFile, vectors: List[PitchVectorSegment], window_size: float, observations: int):
        self.vectors = vectors
        self.mid_file = mid_file
        self.window_size = window_size
        self.observations = observations


def create_dataset_pv() -> Dict[Tuple[float, int], Engine]:
    # initialising LSH hash functions: using random vectors of size 10
    binary_projections = RandomBinaryProjections("rbp", 10)
    vector_map: Dict[Tuple[float, int], Engine] = {}
    available_pitch_vectors = list(pathlib.Path("mid/generated/pitch_vector").glob("**/*.pickle"))
    num_vectors = 0
    for mid in tqdm(available_pitch_vectors):
        with open(mid, "rb") as fh:
            pv_collection: PitchVectorCollection = pickle.load(fh)
        num_vectors += len(pv_collection.vectors)
        pv_spec = (pv_collection.window_size, pv_collection.observations)
        if pv_spec not in vector_map:
            vector_map[pv_spec] = Engine(pv_spec[1])  # i.e observations = dimensions
        for i, vector in enumerate(pv_collection.vectors):
            mid_name = pathlib.Path(pv_collection.mid_file.filename).stem
            vector_map[pv_spec].store_vector(vector.pitch_vector, f"mid {mid_name} " 
                                                                  f"track_offset {vector.start_offset} "
                                                                  f"pitch_modifier {vector.pitch_modifier} ")

    print(f"Done: number of vectors in database is: {num_vectors}")
    return vector_map
