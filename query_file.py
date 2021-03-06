import argparse
import io
import cProfile
import pathlib
import pstats
import time
import datetime


from project.algorithms.graph_based.query_graph_based import query_graph
from project.algorithms.pitch_vector.query_pitch_vector import query_pitch_vector
from project.algorithms.create_datasets import create_dataset_pv, create_dataset_graph
import project.algorithms.core.constants as constants

if __name__ == "__main__":
    start_time = time.time()
    profile = cProfile.Profile()
    profile.enable()

    parser = argparse.ArgumentParser(description="Query the similarity of a MIDI file "
                                                 "to MIDI files already segmented ")
    parser.add_argument("midi_path", type=str, help="Path to query MIDI file")
    parser.add_argument("dataset_folder", type=str, help="Which preprocessed dataset to use. This corresponds to a "
                                                         "folder in mid/generated/<algorithm> containing the relevant "
                                                         "files.")
    parser.add_argument("--algorithm",
                        default=["graph"],
                        nargs=1,
                        choices=["graph", "pitch_vector"],
                        help="Choose which algorithm to run. (default: %(default)s)")

    parser.add_argument("--melody_track", type=int, default=0,
                        help="The track that contains the query file's melody (default: %(default)s)")

    parser.add_argument("--chord_track", type=int, default=None,
                        help="The track that contains the query file's chords, if it exists (default: %(default)s)")

    parser.add_argument("--write_graphs", action="store_true", help="If set, writes the graphs containing "
                                                                    "the query segment connected to the original, "
                                                                    "stored graphs. (this only is relevant for the "
                                                                    "graph based algorithm)")

    parser.add_argument("--use_minimum", action="store_true", help="If set, use the minimum path length between a query"
                                                                   " segment and segments in the MIDI instead of the "
                                                                   "average (this only is relevant for the "
                                                                   "graph based algorithm)")
    parser.add_argument("--pv_veclength", type=int, default=16,
                        help="The size of the projection vectors used for the locality senstive hashing algorithm "
                             "(only relevant to the pitch vector algorithm) (default: %(default)s)")

    parser.add_argument("--show_profiling", action="store_true", help="If set, shows profiling information collected "
                                                                      "from python's cProfile module "
                                                                      "(default: %(default)s)")

    args = parser.parse_args()
    if args.algorithm[0] == "graph":
        print("Graph algorithm chosen: initialising dataset")
        graphs = create_dataset_graph(args.dataset_folder)
        print("Done. Querying starting...")
        query_graph(args.midi_path, args.melody_track, args.use_minimum, args.write_graphs, graphs, args.chord_track)
    elif args.algorithm[0] == "pitch_vector":
        print("Pitch Vector algorithm chosen: initialising dataset")
        pv_collections = create_dataset_pv(args.dataset_folder, args.pv_veclength)
        print("Done. Querying starting...")
        query_pitch_vector(args.midi_path, pv_collections, args.melody_track)

    end_time = time.time()
    print(f"Total time taken was {end_time - start_time}s.")

    profile.disable()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(profile, stream=s).sort_stats(sortby)
    ps.print_stats()
    curr_time = datetime.datetime.now().strftime(constants.TIME_FORMAT)
    pathlib.Path(f"stats/{args.dataset_folder}").mkdir(parents=True, exist_ok=True)
    ps.dump_stats(f"stats/{args.dataset_folder}/{curr_time}_query.stats")
    if args.show_profiling:
        print(s.getvalue())
