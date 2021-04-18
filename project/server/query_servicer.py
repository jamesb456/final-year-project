import pickle
import time
import grpc
import project.server.query_handler_pb2 as query_handler_pb2
import project.server.query_handler_pb2_grpc as query_handler_pb2_grpc
from project.algorithms.pitch_vector.query_pitch_vector import query_pitch_vector
from project.algorithms.graph_based.query_graph_based import query_graph
from project.algorithms.create_datasets import create_dataset_pv, create_dataset_graph


class QueryServicer(query_handler_pb2_grpc.QueryHandlerServicer):
    def __init__(self, graph_dataset: str, pv_dataset: str, pv_veclength: int):
        print("Initialising Pitch Vector Dataset")
        pv_dataset_start = time.time()
        self.vector_dataset = create_dataset_pv(pv_dataset, pv_veclength)
        pv_dataset_end = time.time()
        print(f"Vector dataset loaded. It took {pv_dataset_end - pv_dataset_start}s")

        print("Loading Graph Dataset")
        graph_dataset_start = time.time()
        self.graph_dataset = create_dataset_graph(graph_dataset)
        graph_dataset_end = time.time()
        print(f"Graph dataset loaded. It took {graph_dataset_end - graph_dataset_start}s")

    def QueryGraph(self, request, context):
        time_start = time.time()
        ranking = query_graph(request.query_mid, request.melody_track, request.use_minimum, False, self.graph_dataset,
                              chord_track=request.chord_track)
        time_end = time.time()
        return query_handler_pb2.QueryResponse(ranking=ranking, query_time=time_end-time_start, extra_info={})

    def QueryPitchVector(self, request, context):
        time_start = time.time()
        ranking, vectors = query_pitch_vector(request.query_mid, self.vector_dataset, request.melody_track)
        time_end = time.time()
        return query_handler_pb2.QueryResponse(ranking=ranking, query_time=time_end-time_start, extra_info=vectors)
