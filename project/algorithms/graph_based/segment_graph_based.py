import pathlib
import sys
import time
from typing import Optional

from mido import MidiFile

from project.algorithms.graph_based.midi_graph import MidiGraph
from project.core.lbdm_segmenter import LbdmSegmenter


def segment_graph(midi_path: str, melody_track: int, chord_track: Optional[int], save_combined: bool) -> int:
    time_start = time.time()
    resolved_path = pathlib.Path(midi_path)
    segmenter = LbdmSegmenter()
    mid_file = MidiFile(filename=str(resolved_path))
    mid_name = resolved_path.stem
    print("\n=========================================================")
    print(f"Segmenting {mid_name}.mid to build up a graph of segments:")
    print("=========================================================")
    for (msg1, msg2) in zip(mid_file.tracks[melody_track][1:], mid_file.tracks[melody_track]):
        if (msg1.type == "note_on" and msg2.type == "note_on") \
                or (msg1.type == "note_off" and msg2.type == "note_off"):
            sys.stderr.write(f"Error for Midi File @ {midi_path}: "
                             f"this track is polyphonic, therefore it cannot be processed by this algorithm.\n")
            sys.stderr.flush()
            return -1

    segments = segmenter.create_segments(mid_file, melody_track, chord_track=chord_track)
    print("Done Segmentation")

    mid_location = f"mid/generated/{mid_name}"
    pathlib.Path(mid_location).mkdir(parents=True, exist_ok=True)
    print("Saving original segments to {}...".format(pathlib.Path(mid_location)))

    graph = MidiGraph(mid_file, melody_track, chord_track)

    for (index, segment) in enumerate(segments):
        midi_filepath = str(pathlib.Path(f"{mid_location}/segment_{index}.mid"))
        segment.save_segment(midi_filepath)
        graph.add_identifying_node(midi_filepath)

    print("Starting recursive reduction")

    current_segments = list(enumerate(segments))
    segment_dict = {}
    i = 1
    # recursively apply reduction
    while any([segment.get_number_of_notes() > 1 for _, segment in current_segments]):
        print(f"Beginning reduction number {i}")
        reduced_segments = []
        for (seg_ind, segment) in current_segments:
            # don't reduce if there's only one note left
            if segment.get_number_of_notes() > 1:
                weight, reduced_segment = segment.reduce_segment()
                reduced_filepath = str(pathlib.Path(f"{mid_location}/segment_{seg_ind}_reduction_{i}.mid"))
                reduced_segments.append((seg_ind, reduced_segment))
                reduced_segment.save_segment(filepath=reduced_filepath)
                graph.add_node(filepath=reduced_filepath)
                if i > 1:
                    graph.add_edge(f1=str(pathlib.Path(f"{mid_location}/segment_{seg_ind}_reduction_{i-1}.mid")),
                                   f2=reduced_filepath, weight=weight)
                else:
                    graph.add_edge(f1=str(pathlib.Path(f"{mid_location}/segment_{seg_ind}.mid")),
                                   f2=reduced_filepath, weight=weight)
        segment_dict[i] = reduced_segments
        current_segments = reduced_segments
        i += 1

    print("Done reducing as all segments have at most 1 note.")

    print("Saving graph structure")
    graph.save_to_file(filepath=f"{mid_location}/graph.gpickle")

    combined_dict = {}
    for (iteration, r_segments) in segment_dict.items():
        for (seg_ind, segment) in r_segments:
            if seg_ind not in combined_dict.keys():
                combined_dict[seg_ind] = []
            combined_dict[seg_ind].append(segment)
    if save_combined:
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