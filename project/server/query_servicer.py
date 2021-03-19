import pickle
import time
import grpc
import project.server.query_handler_pb2 as query_handler_pb2
import project.server.query_handler_pb2_grpc as query_handler_pb2_grpc
from project.algorithms.pitch_vector.query_pitch_vector import query_pitch_vector


class QueryServicer(query_handler_pb2_grpc.QueryHandlerServicer):
    def __init__(self):
        pass

    def QueryGraph(self, request, context):
        pass

    def QueryPitchVector(self, request, context):
        print(f"Melody track is {request.melody_track} PLEASE IMPLEMENT THIS!!!")
        time_start = time.time()
        rankings = query_pitch_vector(request.query_mid)
        time_end = time.time()
        return query_handler_pb2.QueryResponse(ranking=rankings, query_time=time_end-time_start)
