import datetime
import json
import pathlib
import sys
import time
import argparse

import grpc
import pandas as pd
import matplotlib.pyplot as plt

from typing import Dict

from tqdm import tqdm

from project.algorithms.core import constants
from project.server.query_handler_pb2_grpc import QueryHandlerStub
from project.server.query_handler_pb2 import VectorArgs, GraphArgs


class QueryResult:
    def __init__(self, query_file: str, algorithm: str, query_time: float, results: Dict):
        self.query_file = query_file
        self.algorithm = algorithm
        self.query_time = query_time
        self.results = results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Test the server with a given set of queries")
    parser.add_argument("algorithm",
                        default=["graph"],
                        nargs=1,
                        choices=["graph", "pitch_vector"],
                        help="Choose which algorithm to test. (default: %(default)s)")

    parser.add_argument("query_set", type=str,
                        help="The name of the set of queries (a folder in mid/queries) which should be used to test "
                             "the given algorithm")

    parser.add_argument("--melody_track", type=int, default=0,
                        help="The track that contains the query file's melody (default: %(default)s)")

    parser.add_argument("--chord_track", default=None,
                        help="The track that contains the query file's chords, if it exists (default: %(default)s)")

    args = parser.parse_args()

    curr_time = datetime.datetime.now().strftime(constants.TIME_FORMAT)
    channel = grpc.insecure_channel('localhost:8007')
    stub = QueryHandlerStub(channel)

    queries = pathlib.Path(f"mid/queries/{args.query_set}")
    if not queries.exists():
        sys.stderr.write(f"Error: the query set {args.query_set} does not exist")
        sys.stderr.flush()
        sys.exit(1)

    available_mids = list(queries.glob("*.mid"))

    query_times = []
    ranks = []
    for mid in tqdm(available_mids):
        if args.algorithm[0] == "graph":
            if args.chord_track is None:
                response = stub.QueryGraph(GraphArgs(query_mid=str(mid), use_minimum=False,
                                                     melody_track=args.melody_track))
            else:
                response = stub.QueryGraph(GraphArgs(query_mid=str(mid), use_minimum=False,
                                                     melody_track=args.melody_track, chord_track=int(args.chord_track)))
        else:
            response = stub.QueryPitchVector(VectorArgs(query_mid=str(mid), melody_track=args.melody_track))

        # find original filename (without .mid or timestamp information)
        # queries are of the format *_<mid_timestamp>.mid
        split_filename = str(mid.stem).split("_")
        # remove last part
        split_filename = split_filename[:len(split_filename) - 1]
        # get original filename back
        original_filename = "".join(split_filename)

        query_times.append(response.query_time)

        df_response = pd.DataFrame(list(response.ranking.items()), columns=["MIDI name", "Distance"])
        # find index of file in response
        mid_position = df_response[df_response["MIDI name"] == original_filename].index
        if len(mid_position) > 0:  # if it was in the list of candidates
            rank = len(df_response.index) - mid_position.item()
            ranks.append(rank)

    ranks = pd.Series(ranks, name="")
    query_times = pd.Series(query_times)
    mean_query_time = query_times.mean()
    len_ranks = len(ranks.index)
    print(f"Mean query time is {mean_query_time}s")
    top_1 = len(ranks[ranks == 1].index) / len_ranks
    top_3 = len(ranks[ranks <= 3].index) / len_ranks
    top_20 = len(ranks[ranks <= 20].index) / len_ranks

    mrr = (1 / ranks).mean()
    print(f"Mean Reciprocal Rank is {mrr}")
    print(f"Top-1 hit rate is {top_1}")
    print(f"Top-3 hit rate is {top_3}")
    print(f"Top-20 hit rate is {top_20}")


    # df_vec = pd.DataFrame(list(response_vec.ranking.items()), columns=["MIDI name", "Similarity"])
    # df_graph = pd.DataFrame(list(response_graph.ranking.items()), columns=["MIDI name", "Similarity"])
    #
    # top20_vec = df_vec.tail(20)
    # top20_graph = df_graph.tail(20)
    # print(list(top20_vec.items()))
    # print(list(top20_graph.items()))
    #
    # fig, axes = plt.subplots(1, 2)
    # fig.suptitle("Comparison of Top 20 most similar songs as returned by each algorithm")
    #
    # top20_vec.plot(x="MIDI name", kind="barh", ax=axes[0],
    #                title=f"Pitch Vector (Dynamic Time Warping edition) : distance between aligned sequences "
    #                      f"(lower is better)")
    # axes[0].set_xlabel("Distance (lower is better)")
    # top20_graph.plot(x="MIDI name", kind="barh", ax=axes[1],
    #                  title=f"Graph: avg distance between query and song segments(lower is better)")
    # axes[1].set_xlabel("avg distance between song segments and query segment (lower is better)")
    # plt.show()
    #
    # res1 = QueryResult(query, "graph", response_graph.query_time,
    #                    top20_graph[::-1].reset_index(drop=True).to_dict("index"))
    # res2 = QueryResult(query, "pitch_vector", response_vec.query_time,
    #                    top20_vec[::-1].reset_index(drop=True).to_dict("index"))
    #
    # with open(f"query_output/rankings/{curr_time}_graph.json", "w") as fh1:
    #     json.dump(res1.__dict__, fh1, indent=4)
    #
    # with open(f"query_output/rankings/{curr_time}_pv.json", "w") as fh2:
    #     json.dump(res2.__dict__, fh2, indent=4)


