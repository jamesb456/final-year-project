import pathlib, argparse

from mido import MidiFile

from project.algorithms.graph_based.reduction import reduce_segment
from project.segment.lbdm_segmenter import LbdmSegmenter
from project.util.midtools import get_track_time_signatures
from project.visualisation.graph import lbdm_graph


# temp: could use classes eventually
def segment_vector(filepath: str, melody_track: int, chord_track: int = 1):
    pass


def segment_graph(midi_path: str, melody_track: int, chord_track: int = 1):
    segmenter = LbdmSegmenter()
    mid_file = MidiFile(filename=midi_path)
    mid_name = pathlib.Path(midi_path).stem
    print(f"Segmenting {mid_name}.mid to build up a graph of segments:")
    segments = segmenter.create_segments(mid_file, melody_track)
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

    combined_dict = {}
    for (iteration, r_segments) in segment_dict.items():
        print(f"\tSaving iteration {iteration}")
        for (seg_ind, segment) in r_segments:
            segment.save_segment(filepath=f"{mid_location}/segment_{seg_ind}_reduction_{iteration}.mid")
            if seg_ind not in combined_dict.keys():
                combined_dict[seg_ind] = []
            combined_dict[seg_ind].append(segment)

    print("Saving combined segments...")

    for (segment_index, indexed_segments) in combined_dict.items():
        old_file = indexed_segments[0].file
        new_file = MidiFile(type=old_file.type, ticks_per_beat=old_file.ticks_per_beat, charset=old_file.charset,
                            debug=old_file.debug, clip=old_file.clip)
        original_track = new_file.add_track()
        segments[segment_index].copy_notes_to_track(original_track)
        for segment in indexed_segments:
            track = new_file.add_track()
            segment.copy_notes_to_track(track)

        new_file.save(filename=f"{mid_location}/combined_segment_{segment_index}.mid")

    print("Segments saved.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split a MIDI file into several segments "
                                                 "so it may be queried for similarity")
    parser.add_argument("midi_path", type=str, help="Path to MIDI file to segment")
    parser.add_argument("--algorithm",
                        default="graph",
                        nargs=1,
                        choices=["graph", "pitch_vector"],
                        help="Choose which algorithm to run. (default: %(default)s)")
    parser.add_argument("--melody_track", type=int, default=0,
                        help="The track the file should be segmented with respect to (default: %(default)s)")
    parser.add_argument("--chord_track", type=int, nargs="?",
                        help="The track containing the chords in the MIDI file (if such a track exists)")

    args = parser.parse_args()

    if args.algorithm[0] == "graph":
        segment_graph(args.midi_path, args.melody_track)
    elif args.algorithm[0] == "pitch_vector":
        raise NotImplementedError("Pitch vector algorithm chosen, but this is not implemented yet.")
    else:
        raise ValueError("Unrecognised algorithm choice")

