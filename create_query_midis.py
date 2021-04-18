import pathlib
import sys

from tqdm import tqdm

from project.algorithms.create_queries import create_indexed_queries, create_modified_queries, create_random_queries
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a series of query from a set of MIDI files based on several"
                                                 " strategies.")
    parser.add_argument("mid_dataset", help="A path to a folder containing MIDI files to create the queries from.")
    parser.add_argument("number_of_queries", help="The number of query MIDI files to generate "
                                                  "(default: %(default)s)", type=int, default=400)
    parser.add_argument("output_name", help="The name of the folder these MIDIs should be placed in. This folder "
                                            "will be created in mid\\queries")
    parser.add_argument("--rng_seed", help="The seed to be used for any random number generation "
                                           "(default: %(default)s)", default=None)

    strategies = parser.add_subparsers(title="query_strategies", dest="query_strategy", required=True)

    indexed_parser = strategies.add_parser("indexed",
                                           help="Create query MIDIs based on the segmentation algorithm"
                                                " used by each QBE algorithm")

    modified_ind_parser = strategies.add_parser("indexed_mod",
                                                help="Create query MIDIs based on the segmentation algorithm"
                                                     " used by each QBE algorithm, which are also modified so"
                                                     " they are not exactly the same (e.g. a different tempo)")

    random_parser = strategies.add_parser("random",
                                          help="Create query MIDIs based on random length sections of the input"
                                               " files.")

    # indexed parser arguments
    indexed_parser.add_argument("--algorithm",
                                default=["graph"],
                                nargs=1,
                                choices=["graph", "pitch_vector"],
                                help="Choose which algorithm to create segments for. (default: %(default)s)")

    indexed_parser.add_argument("--melody_track",
                                type=int,
                                default=0,
                                help="The MIDI track to create the segments from. (default: %(default)s)")

    indexed_parser.add_argument("--chord_track",
                                type=int,
                                default=None,
                                help="The track containing the chords in the MIDI file (useful only for the graph"
                                     "algorithm, if such a track exists. (default: %(default)s) ")

    indexed_parser.add_argument("--time",
                                type=float,
                                default=3,
                                help="If the pitch vector algorithm is chosen, the length (in seconds) of each segment "
                                     "(default: %(default)ss)")

    # modified_ind parser arguments

    modified_ind_parser.add_argument("--algorithm",
                                     default=["graph"],
                                     nargs=1,
                                     choices=["graph", "pitch_vector"],
                                     help="Choose which algorithm to create segments for. (default: %(default)s)")

    modified_ind_parser.add_argument("--melody_track",
                                     type=int,
                                     default=0,
                                     help="The MIDI track to create the segments from. (default: %(default)s)")

    modified_ind_parser.add_argument("--chord_track",
                                     type=int,
                                     default=None,
                                     help="The track containing the chords in the MIDI file (useful only for the graph"
                                          "algorithm, if such a track exists. (default: %(default)s) ")

    modified_ind_parser.add_argument("--time",
                                     type=float,
                                     default=3,
                                     help="If the pitch vector algorithm is chosen, the length (in seconds) "
                                          "of each segment (default: %(default)ss)")

    modified_ind_parser.add_argument("--transpose",
                                     type=int,
                                     default=0,
                                     help=" The pitch (in semitones) to adjust each note by."
                                          " (default: %(default)ss)")

    modified_ind_parser.add_argument("--duration_transform",
                                     type=float,
                                     default=1,
                                     help=" The amount to scale the duration of each note by."
                                          " (default: %(default)s)")

    modified_ind_parser.add_argument("--extra_notes",
                                     type=float,
                                     default=0,
                                     help=" The number of extra noise notes to be added to each segment. The pitch"
                                          " of these notes is taken from a normal distribution with the mean pitch of "
                                          " the original segment being the mean of the distribution. "
                                          " (default: %(default)s)")

    modified_ind_parser.add_argument("--removed_notes",
                                     type=float,
                                     default=0,
                                     help=" The number of removed notes to be removed from each segment. "
                                          " (default: %(default)s)")
    # random parser arguments
    # TODO: complete this

    args = parser.parse_args()
    output_path = pathlib.Path(f"mid/queries/{args.output_name}")
    try:
        output_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        sys.stderr.write(f"Error: the folder {str(output_path)} already exists. Please delete this folder or choose a "
                         f"different name for the output folder.")
        sys.stderr.flush()
        sys.exit(1)

    segments = []
    if args.query_strategy == "indexed" or args.query_strategy == "indexed_mod":

        segmenter_args = {}
        if args.chord_track is not None:
            segmenter_args["chord_track"] = args.chord_track

        if args.time is not None:
            segmenter_args["time"] = args.time
        if args.query_strategy == "indexed":
            print("Indexed segments chosen")
            segments = create_indexed_queries(args.algorithm[0], args.number_of_queries, args.mid_dataset,
                                              args.melody_track, args.rng_seed, segmenter_args=segmenter_args)
        else:
            print("Indexed (modified) segments chosen")
            segments = create_modified_queries(args.algorithm[0], args.number_of_queries, args.mid_dataset,
                                               args.melody_track, args.rng_seed,
                                               args.transpose, args.duration_transform, args.extra_notes,
                                               args.removed_notes, segmenter_args=segmenter_args)
    elif args.query_strategy == "random":
        print("Random segments chosen")
        raise NotImplementedError("Not implemented yet")
    else:
        raise ValueError(f"Unknown querying strategy {args.query_strategy}")

    if len(segments) > 0:
        print(f"Chosen {len(segments)} segments from the list. Saving them now:")
        for segment in tqdm(segments, "Saving segments"):
            segment.save_as_midi(f"{output_path}/{segment.filename}_{segment.start_time}.mid")
