import argparse
import io
import cProfile
import pstats
import time

from project.algorithms.graph_based.query_graph_based import query_graph

if __name__ == "__main__":
    start_time = time.time()
    profile = cProfile.Profile()
    profile.enable()

    parser = argparse.ArgumentParser(description="Query the similarity of a MIDI file "
                                                 "to MIDI files already segmented ")
    parser.add_argument("midi_path", type=str, help="Path to query MIDI file")
    parser.add_argument("--write_graphs", action="store_true", help="If set, writes the graphs containing "
                                                                    "the query segment connected to the original, "
                                                                    "stored graphs.")
    parser.add_argument("--use_minimum", action="store_true", help="If set, use the minimum path length between a query"
                                                                   " segment and segments in the MIDI instead of the "
                                                                   "average.")

    args = parser.parse_args()
    query_graph(args.midi_path, args.use_minimum, args.write_graphs)

    profile.disable()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(profile, stream=s).sort_stats(sortby)
    ps.print_stats()
    ps.dump_stats("query.stats")
    print(s.getvalue())
    end_time = time.time()
    print(f"Total time taken was {end_time - start_time}s.")


