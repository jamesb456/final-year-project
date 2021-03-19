from concurrent import futures

import grpc
import project.server.query_handler_pb2 as query_handler_pb2
import project.server.query_handler_pb2_grpc as query_handler_pb2_grpc
from project.server.query_servicer import QueryServicer

if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    query_handler_pb2_grpc.add_QueryHandlerServicer_to_server(
        QueryServicer(), server)
    server.add_insecure_port('[::]:8007')  # ipv6
    server.start()
    server.wait_for_termination()
