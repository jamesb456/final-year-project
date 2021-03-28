import json
import time

import grpc
import pandas as pd
import matplotlib.pyplot as plt

from typing import Dict
from project.server.query_handler_pb2_grpc import QueryHandlerStub
from project.server.query_handler_pb2 import VectorArgs, GraphArgs


class QueryResult:
    def __init__(self, query_file: str, algorithm: str, query_time: float, results: Dict):
        self.query_file = query_file
        self.algorithm = algorithm
        self.query_time = query_time
        self.results = results


if __name__ == '__main__':
    curr_time = time.strftime("%Y%m%d_%I%M%S")
    channel = grpc.insecure_channel('localhost:8007')
    stub = QueryHandlerStub(channel)
    query = "mid/generated/graph/ashover8/segment_0.mid"
    print(f"Asking server for similarity rankings for {query} with notes from track 0")

    print("Pitch Vector Algorithm")
    response_vec = stub.QueryPitchVector(VectorArgs(query_mid=query, melody_track=0))
    print("Done. Graph based algorithm")
    response_graph = stub.QueryGraph(GraphArgs(query_mid=query, use_minimum=False, melody_track=0))

    print(f"The time to query (on the servers end) was \n(pitch vector) {response_vec.query_time}s\n"
          f"(graph) {response_graph.query_time}s")

    df_vec = pd.DataFrame(list(response_vec.ranking.items()), columns=["MIDI name", "Similarity"])
    df_graph = pd.DataFrame(list(response_graph.ranking.items()), columns=["MIDI name", "Similarity"])

    top20_vec = df_vec.tail(20)
    top20_graph = df_graph.tail(20)
    print(list(top20_vec.items()))
    print(list(top20_graph.items()))

    fig, axes = plt.subplots(1, 2)
    fig.suptitle("Comparison of Top 20 most similar songs as returned by each algorithm")

    top20_vec.plot(x="MIDI name", kind="barh", ax=axes[0],
                   title=f"Pitch Vector (Dynamic Time Warping edition) : distance between aligned sequences "
                         f"(lower is better)")
    axes[0].set_xlabel("Distance (lower is better)")
    top20_graph.plot(x="MIDI name", kind="barh", ax=axes[1],
                     title=f"Graph: avg distance between query and song segments(lower is better)")
    axes[1].set_xlabel("avg distance between song segments and query segment (lower is better)")

    res1 = QueryResult(query, "graph", response_graph.query_time,
                       top20_graph[::-1].reset_index(drop=True).to_dict("index"))
    res2 = QueryResult(query, "pitch_vector", response_vec.query_time,
                       top20_vec[::-1].reset_index(drop=True).to_dict("index"))

    with open(f"query_output/rankings/{curr_time}_graph.json", "w") as fh1:
        json.dump(res1.__dict__, fh1, indent=4)

    with open(f"query_output/rankings/{curr_time}_pv.json", "w") as fh2:
        json.dump(res2.__dict__, fh2, indent=4)

    plt.show()

