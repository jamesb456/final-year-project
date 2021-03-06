import json
import pathlib
import sys
import time
import pickle
from typing import Optional

from mido import MidiFile

from project.algorithms.core.chord import Chord
from project.algorithms.graph_based.midi_graph import MidiGraph
from project.algorithms.graph_based.lbdm_segmenter import LbdmSegmenter
from project.algorithms.core.midtools import is_note_on, is_note_off, is_monophonic


def segment_graph(midi_path: str, melody_track: int, output_folder: str,
                  chord_track: Optional[int], save_combined: bool) -> int:
    time_start = time.time()

    resolved_path = pathlib.Path(midi_path)
    segmenter = LbdmSegmenter()
    mid_file = MidiFile(filename=str(resolved_path))
    mid_name = resolved_path.stem
    print("\n=========================================================")
    print(f"Segmenting {mid_name}.mid to build up a graph of segments:")
    print("=========================================================")
    if not is_monophonic(mid_file.tracks[melody_track]):
        sys.stderr.write(f"Error for Midi File @ {midi_path}: "
                         f"this track is polyphonic, therefore it cannot be processed by this algorithm.\n")
        sys.stderr.flush()
        return -1

    segments = segmenter.create_segments(mid_file, melody_track, chord_track=chord_track)
    print("Done Segmentation")

    mid_location = f"mid/generated/graph/{output_folder}/{mid_name}"
    pathlib.Path(mid_location).mkdir(parents=True, exist_ok=True)

    graph = MidiGraph(mid_file, melody_track, chord_track)

    for (index, segment) in enumerate(segments):
        midi_filepath = str(pathlib.Path(f"{mid_location}/midi_segments/segment_{index}.mid"))
        graph.add_identifying_node(midi_filepath, segment)

    print("Starting recursive reduction")

    segments_and_indices = list(enumerate(segments))
    segment_dict = {}
    i = 1
    # recursively apply reduction
    while any([segment.get_number_of_notes() > 1 for _, segment in segments_and_indices]):
        print(f"Beginning reduction number {i}")
        reduced_segments = []  # current segments and indices of those segments to be reduced
        for (seg_ind, segment) in segments_and_indices:
            # don't reduce if there's only one note left
            if segment.get_number_of_notes() > 1:
                weight, reduced_segment = segment.reduce_segment()
                reduced_filepath = str(pathlib.Path(f"{mid_location}/midi_segments/segment_{seg_ind}_reduction_{i}.mid"))
                reduced_segments.append((seg_ind, reduced_segment))
                graph.add_node(reduced_filepath, reduced_segment)
                if i > 1:
                    graph.add_edge(
                        n1=str(pathlib.Path(f"{mid_location}/midi_segments/segment_{seg_ind}_reduction_{i - 1}.mid")),
                        n2=reduced_filepath, weight=weight)
                else:
                    graph.add_edge(n1=str(pathlib.Path(f"{mid_location}/midi_segments/segment_{seg_ind}.mid")),
                                   n2=reduced_filepath, weight=weight)
        segment_dict[i] = reduced_segments
        segments_and_indices = reduced_segments
        i += 1

    print("Done reducing as all segments have at most 1 note.")
    print("Saving graph structure")
    with open(str(pathlib.Path(f"{mid_location}/graph.gpickle")), "wb") as fh:
        pickle.dump(graph, fh, protocol=pickle.HIGHEST_PROTOCOL)
    print("Graph saved")

    if save_combined:
        combined_dict = {}
        for (iteration, r_segments) in segment_dict.items():
            for (seg_ind, segment) in r_segments:
                if seg_ind not in combined_dict.keys():
                    combined_dict[seg_ind] = []
                combined_dict[seg_ind].append(segment)
        print("--saved_combined specified: saving combined segments...")
        for (segment_index, indexed_segments) in combined_dict.items():
            new_file = MidiFile(**indexed_segments[0].get_file_metadata())
            original_track = new_file.add_track()
            segments[segment_index].copy_notes_to_track(original_track)
            for segment in indexed_segments:
                track = new_file.add_track()
                segment.copy_notes_to_track(track)

            new_file.save(filename=f"{mid_location}/combined_segment_{segment_index}.mid")
        print("Combined segments saved.")

    time_end = time.time()
    print(f"Time elapsed: {time_end - time_start} seconds")
    return 0
