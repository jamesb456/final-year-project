import grpc
import pandas as pd
import matplotlib.pyplot as plt
from project.server.query_handler_pb2_grpc import QueryHandlerStub
from project.server.query_handler_pb2 import VectorArgs, GraphArgs
if __name__ == '__main__':
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
                   title=f"Pitch Vector (no recursive alignment) : number of matches (higher is better)")
    axes[0].set_xlabel("Number of matches (higher is better)")
    top20_graph.plot(x="MIDI name", kind="barh", ax=axes[1],
                     title=f"Graph: avg distance between query and song segments(lower is better)")
    axes[1].set_xlabel("Average distance between song segments and query segment (lower is better)")
    plt.show()
