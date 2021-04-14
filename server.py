import argparse
from concurrent import futures

import grpc
import project.server.query_handler_pb2 as query_handler_pb2
import project.server.query_handler_pb2_grpc as query_handler_pb2_grpc
from project.server.query_servicer import QueryServicer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A server to service incoming MIDI query requests.")
    parser.add_argument("graph_dataset", type=str, help="The dataset of segmented pieces of music to use "
                                                        "when the graph algorithm is being used")
    parser.add_argument("pv_dataset", type=str, help="The dataset of segmented pieces of music to use "
                                                     "when the pitch vector algorithm is being used")
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    query_handler_pb2_grpc.add_QueryHandlerServicer_to_server(
        QueryServicer(args.graph_dataset, args.pv_dataset), server)
    server.add_insecure_port('[::]:8007')  # ipv6
    server.start()
    server.wait_for_termination()
