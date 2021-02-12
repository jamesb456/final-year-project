import pathlib, argparse

from mido import MidiFile

from project.algorithms.graph_based.reduction import reduce_segment
from project.segment.lbdm_segmenter import LbdmSegmenter
from project.util.midtools import get_track_time_signatures
from project.visualisation.graph import lbdm_graph

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Segment and create a graph representation of a MIDI file.")
    parser.add_argument("midi_path", type=str, help="Path to MIDI file to segment")
    parser.add_argument("--melody_track", type=int, default=0,
                        help="The track the file should be segmented with respect to")



    args = parser.parse_args()
    mid_file = MidiFile(filename=args.midi_path)
    lbdm_graph(mid_file.tracks[0],mid_file.ticks_per_beat)
    segmenter = LbdmSegmenter()

    mid_name = pathlib.Path(args.midi_path).stem
    print(f"Segmenting {mid_name}.mid")
    segments = segmenter.create_segments(mid_file, args.melody_track)
    print("Done Segmentation")

    mid_location = f"mid/generated/{mid_name}"
    pathlib.Path(mid_location).mkdir(parents=True, exist_ok=True)
    print("Saving original segments to {}...".format(pathlib.Path(mid_location).resolve()))

    for (index, segment) in enumerate(segments):
        segment.save_segment(f"{mid_location}/segment_{index}.mid")

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
                reduced_segments.append((seg_ind, reduce_segment(segment)))
        segment_dict[i] = reduced_segments
        current_segments = reduced_segments
        i += 1

    print("Done reducing as all segments have at most 1 note.")
    print("Saving segments...")

    for (iteration, segments) in segment_dict.items():
        print(f"\tFor iteration {iteration}")
        for (seg_ind, segment) in segments:
            segment.save_segment(filepath=f"{mid_location}/segment_{seg_ind}_reduction_{iteration}.mid")

    print("Segments saved.")