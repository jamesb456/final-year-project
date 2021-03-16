import pathlib
import time

from typing import Optional

from mido import MidiFile

from project.core.segment.pitch_vector_segmenter import PitchVectorSegmenter


def segment_pitch_vector(midi_path: str, melody_track: int, window_size: float = 3.0, num_observations: int = 20) -> int:
    time_start = time.time()
    resolved_path = pathlib.Path(midi_path)
    segmenter = PitchVectorSegmenter(window_size, num_observations)
    mid_file = MidiFile(filename=str(resolved_path))
    mid_name = resolved_path.stem
    print("\n=========================================================")
    print(f"Segmenting {mid_name}.mid into several pitch vectors:")
    print("=========================================================")

    segments = segmenter.create_segments(mid_file, melody_track)

    time_end = time.time()
    return 0
