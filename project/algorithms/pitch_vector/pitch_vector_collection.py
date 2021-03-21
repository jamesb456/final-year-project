import pathlib
import pickle
from collections import defaultdict
from typing import List, Dict, Tuple

from mido import MidiFile
from tqdm import tqdm
from project.core.segment.pitch_vector_segment import PitchVectorSegment


class PitchVectorCollection:
    def __init__(self, mid_file: MidiFile, vectors: List[PitchVectorSegment], window_size: float, observations: int):
        self.vectors = vectors
        self.mid_file = mid_file
        self.window_size = window_size
        self.observations = observations


def create_dataset_pv() -> Dict[Tuple[float, int], List[PitchVectorCollection]]:
    vector_map = defaultdict(list)
    available_mids = list(pathlib.Path("mid/generated/pitch_vector").glob("**/*.pickle"))
    num_vectors = 0
    for mid in tqdm(available_mids):
        with open(mid, "rb") as fh:
            pv_collection: PitchVectorCollection = pickle.load(fh)
        num_vectors += len(pv_collection.vectors)
        vector_map[(pv_collection.window_size, pv_collection.observations)].append(pv_collection)
    print(f"Done: number of vectors in database is: {num_vectors}")
    return vector_map
