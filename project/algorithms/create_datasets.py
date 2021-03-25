import pathlib
import pickle
from typing import Dict, Tuple, List

from nearpy import Engine
from nearpy.distances.euclidean import EuclideanDistance
from nearpy.hashes import RandomBinaryProjectionTree
from tqdm import tqdm

from project.algorithms.graph_based.midi_graph import MidiGraph
from project.algorithms.pitch_vector.pitch_vector_collection import PitchVectorCollection


def create_dataset_pv() -> Dict[Tuple[float, int], Engine]:
    # initialising LSH hash functions
    binary_proj_1 = RandomBinaryProjectionTree("rbpt", 20, 20)

    vector_map: Dict[Tuple[float, int], Engine] = {}
    available_pitch_vectors = list(pathlib.Path("mid/generated/pitch_vector").glob("**/*.pickle"))
    num_vectors = 0
    for mid in tqdm(available_pitch_vectors):
        with open(mid, "rb") as fh:
            pv_collection: PitchVectorCollection = pickle.load(fh)
        num_vectors += len(pv_collection.vectors)
        pv_spec = (pv_collection.window_size, pv_collection.observations)
        if pv_spec not in vector_map:
            vector_map[pv_spec] = Engine(pv_spec[1], lshashes=[binary_proj_1],
                                         distance=EuclideanDistance())
            # i.e observations = dimensions
        for i, vector in enumerate(pv_collection.vectors):
            vector_map[pv_spec].store_vector(vector.pitch_vector, (pv_collection.mid_file, vector.start_offset,
                                                                   vector.pitch_modifier, pv_collection.melody_track))

    print(f"Done: number of vectors in database is: {num_vectors}")
    return vector_map


def create_dataset_graph() -> List[MidiGraph]:
    available_graphs = list(pathlib.Path("mid/generated/graph").glob("**/*.gpickle"))
    graphs = []
    for gpickle in tqdm(available_graphs):
        graph = MidiGraph.from_gpickle(str(gpickle))
        graph.load_notes_for_segments(str(pathlib.Path(gpickle).parents[0]))
        graphs.append(graph)

    return graphs
