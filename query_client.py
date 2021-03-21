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

    print(f"Rankings: Vector {response_vec.ranking}\n{response_graph.ranking} ")
