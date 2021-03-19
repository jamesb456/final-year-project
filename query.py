import argparse
import io
import cProfile
import pstats
import time
import datetime

from project.algorithms.graph_based.query_graph_based import query_graph
from project.algorithms.pitch_vector.query_pitch_vector import query_pitch_vector

if __name__ == "__main__":
    start_time = time.time()
    profile = cProfile.Profile()
    profile.enable()

    parser = argparse.ArgumentParser(description="Query the similarity of a MIDI file "
                                                 "to MIDI files already segmented ")
    parser.add_argument("midi_path", type=str, help="Path to query MIDI file")
    parser.add_argument("--algorithm",
                        default=["graph"],
                        nargs=1,
                        choices=["graph", "pitch_vector"],
                        help="Choose which algorithm to run. (default: %(default)s)")
    parser.add_argument("--write_graphs", action="store_true", help="If set, writes the graphs containing "
                                                                    "the query core connected to the original, "
                                                                    "stored graphs. (this only is relevant for the "
                                                                    "graph based algorithm)")
    parser.add_argument("--use_minimum", action="store_true", help="If set, use the minimum path length between a query"
                                                                   " core and segments in the MIDI instead of the "
                                                                   "average (this only is relevant for the "
                                                                   "graph based algorithm)")

    args = parser.parse_args()
    if args.algorithm[0] == "graph":
        query_graph(args.midi_path, args.use_minimum, args.write_graphs)
    elif args.algorithm[0] == "pitch_vector":
        query_pitch_vector(args.midi_path)

    profile.disable()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(profile, stream=s).sort_stats(sortby)
    ps.print_stats()
    curr_time = datetime.datetime.now().strftime("%Y%m%d_%I%M%S")
    ps.dump_stats(f"stats/{curr_time}_query.stats")
    print(s.getvalue())
    end_time = time.time()
    print(f"Total time taken was {end_time - start_time}s.")
