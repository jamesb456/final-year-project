import pathlib
import time
from collections import defaultdict, OrderedDict

import json
import numpy as np
import pandas as pd

from typing import Dict, Tuple
from mido import MidiFile, tick2second
from nearpy import Engine
from tqdm import tqdm

from project.algorithms.pitch_vector.pitch_vector_segmenter import PitchVectorSegmenter
from project.algorithms.pitch_vector.recursive_alignment import recursive_alignment
from project.algorithms.pitch_vector.vector_candidate import VectorCandidate
from project.algorithms.core.midtools import get_start_offset, get_end_offset, get_note_timeline, \
    get_notes_in_time_range


def query_pitch_vector(midi_path: str, vector_map: Dict[Tuple[float, int], Engine],
                       melody_track: int = 0) -> Tuple[Dict[str, float], Dict[str, str]]:
    """
    Run *Query by Example*, trying to guess the parent song of the MIDI file located at ``midi_path``,
    with a known set of pitch vectors, each associated with a song, being used.

    Args:
        midi_path: The path to the Query MIDI file that we want to find the parent song of.
        melody_track: The track containing the melody of the MIDI at midi_path
        vector_map: A list of Engines containing pitch vectors with different observations and window sizes

    Returns:
        A (ranking, extra) pair. ranking contains the distance between the query and each known file in the indexed dataset.
        extra is extra information about which exact vector had the smallest distance
    """

    # build up database of pitch vectors
    # then segment the query based on the different window sizes and observations
    # in the database Engine

    query_mid = MidiFile(midi_path)
    query_track = query_mid.tracks[melody_track]
    query_start, start_index = get_start_offset(query_track, query_mid.ticks_per_beat)
    query_end, end_index = get_end_offset(query_track, query_mid.ticks_per_beat)
    query_notes = get_notes_in_time_range(query_track, query_mid.ticks_per_beat, query_start, query_end)
    query_mean_pitch = sum(map(lambda n: n.pitch, query_notes)) / len(query_notes)
    query_notes_norm = list(map(lambda n: n.normalize(query_mean_pitch, query_start, query_end), query_notes))

    print("Compare the query segment with the database of vectors")

    similarity_map = {}
    matched_vectors = {}
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
                for vec, (mid_file, cand_offset, pitch_mod, cand_track), distance in neighbours:
                    candidates.append(VectorCandidate(query_segment.start_offset, modifier, cand_offset,
                                                      mid_file, cand_track))

        print(f"Done finding candidates. Number of them is: {len(candidates)}")

        for candidate in tqdm(candidates, desc="Testing candidate segments"):
            start, end = candidate.get_candidate_segment_bounds(query_start, query_end)
            song_track = candidate.song_ident.tracks[candidate.song_track]
            candidate_notes = get_notes_in_time_range(song_track, candidate.ticks_per_beat, start, end)
            mean_pitch = sum(map(lambda n: n.pitch, candidate_notes)) / len(candidate_notes)
            norm_notes = list(map(lambda n: n.normalize(mean_pitch, start, end - start), candidate_notes))
            dist = recursive_alignment(query_notes_norm, norm_notes, [(0.45, 0.45), (0.5, 0.5), (0.55, 0.55)], 2)

            song_name = pathlib.Path(candidate.song_ident.filename).stem
            if song_name not in similarity_map:
                similarity_map[song_name] = dist
                matched_vectors[song_name] = f"{start} {end} {candidate.window_modifier}"
            else:
                min_value = min(similarity_map[song_name],
                                dist)
                similarity_map[song_name] = min_value
                if min_value == dist:
                    matched_vectors[song_name] = f"{start} {end} {candidate.window_modifier}"

    sorted_dict = {k: v for k, v in sorted(similarity_map.items(), key=lambda item: item[1], reverse=True)}
    series = pd.Series(sorted_dict)
    pathlib.Path(f"query_output/rankings").mkdir(exist_ok=True, parents=True)
    series.to_csv(f"query_output/rankings/{pathlib.Path(midi_path).stem}.csv")
    for index, (mid_file, similarity) in enumerate(sorted_dict.items()):
        print(f"\t[{len(similarity_map.items()) - index}] {mid_file}: {similarity}")

    return sorted_dict, matched_vectors
