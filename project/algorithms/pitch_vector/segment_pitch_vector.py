import pathlib
import pickle
import time

from mido import MidiFile

from project.algorithms.pitch_vector.pitch_vector_collection import PitchVectorCollection
from project.algorithms.pitch_vector.pitch_vector_segmenter import PitchVectorSegmenter


def segment_pitch_vector(midi_path: str, melody_track: int, output_folder: str,
                         window_size: float = 3.0, num_observations: int = 20) -> int:
    time_start = time.time()
    resolved_path = pathlib.Path(midi_path)
    segmenter = PitchVectorSegmenter(window_size, num_observations)
    mid_file = MidiFile(filename=str(resolved_path))
    mid_name = resolved_path.stem
    print("\n=========================================================")
    print(f"Segmenting {mid_name}.mid into several pitch vectors:")
    print("=========================================================")

    segments = segmenter.create_segments(mid_file, melody_track)
    mid_location = f"mid/generated/pitch_vector/{output_folder}/{mid_name}"
    pathlib.Path(mid_location).mkdir(parents=True, exist_ok=True)
    pv_collection = PitchVectorCollection(mid_file, segments, window_size, num_observations, melody_track)
    with open(f"{mid_location}/pitch_vectors.pickle", "wb") as file:
        pickle.dump(pv_collection, file, pickle.HIGHEST_PROTOCOL)
    time_end = time.time()
    print(f"Done. Created {len(segments)} vectors ( window size of {window_size}s with {num_observations} dimensions)")
    print(f"It took {time_end - time_start} seconds")
    return 0
