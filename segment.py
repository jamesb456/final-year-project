import argparse
import sys
import time
import datetime
import glob
import cProfile
import pstats
import io
from typing import Optional

from project.algorithms.graph_based.segment_graph_based import segment_graph
from project.algorithms.pitch_vector.segment_pitch_vector import segment_pitch_vector

if __name__ == '__main__':
    prof = cProfile.Profile()
    prof.enable()
    parser = argparse.ArgumentParser(description="Split a MIDI file into several segments "
                                                 "so it may be queried for similarity")
    parser.add_argument("midi_paths", nargs="+", type=str, help="Path to MIDI file(s) to core")
    parser.add_argument("--algorithm",
                        default=["graph"],
                        nargs=1,
                        choices=["graph", "pitch_vector"],
                        help="Choose which algorithm to run. (default: %(default)s)")
    parser.add_argument("--melody_track", type=int, default=0,
                        help="The track the file should be segmented with respect to (default: %(default)s)")
    parser.add_argument("--chord_track", type=int, nargs="?",
                        help="The track containing the chords in the MIDI file (if such a track exists) (only "
                             "relevant for the graph based algorithm)")
    parser.add_argument("--show_profiling", action="store_true", help="If set, shows profiling information collected "
                                                                      "from python's cProfile module")

    parser.add_argument("--save_combined", action="store_true", help="If set and running the graph algorithm, "
                                                                     "saves all of the reductions of each core "
                                                                     "into one MIDI file (as well as the usual reduced "
                                                                     "segments normally)")

    args = parser.parse_args()
    err_count = 0
    count = 0
    time_taken = 0
    paths = []
    for mid_path in args.midi_paths:
        globbed_paths = glob.glob(mid_path)
        for path in globbed_paths:
            paths.append(path)

    if len(paths) == 0:
        sys.stderr.write("Error: no MIDI files correspond to the path(s) given\n")
        sys.stderr.flush()

    if args.algorithm[0] == "graph":
        graph_start = time.time()

        for path in paths:
            result = segment_graph(path, args.melody_track, args.chord_track, args.save_combined)
            if result != 0:
                err_count += 1
            count += 1

        graph_end = time.time()
        time_taken = graph_end - graph_start

    elif args.algorithm[0] == "pitch_vector":
        vector_start = time.time()

        for path in paths:
            result = segment_pitch_vector(path, args.melody_track)
            if result != 0:
                err_count += 1
            count += 1

        vector_end = time.time()
        time_taken = vector_end - vector_start

    else:
        raise ValueError(f"Unrecognised algorithm choice {args.algorithm[0]}")

    print(f"\n\nDone segmenting all {count} mid files. Total time taken was {time_taken} seconds.")
    sys.stderr.write(f"Total unprocessed files due to errors is: {err_count}\n")

    prof.disable()
    if args.show_profiling:
        print("--show_profiling specified: Profiling info below")
        s = io.StringIO()
        sortby = pstats.SortKey.CUMULATIVE
        ps = pstats.Stats(prof, stream=s).sort_stats(sortby)
        ps.print_stats()
        curr_time = datetime.datetime.now().strftime("%Y%m%d_%I%M%S")
        ps.dump_stats(f"{curr_time}_segment.stats")
        print(s.getvalue())

        print(f"\nSaved these stats to {curr_time}_segment.stats.")
