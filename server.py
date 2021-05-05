import argparse
import pathlib
import sys
from concurrent import futures

import grpc
import project.server.query_handler_pb2 as query_handler_pb2
import project.server.query_handler_pb2_grpc as query_handler_pb2_grpc
from project.server.query_servicer import QueryServicer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A server to service incoming MIDI query requests.")
    parser.add_argument("--graph_index", type=str, help="The dataset of segmented pieces of music to use "
                                                        "when the graph algorithm is being used")

    parser.add_argument("--pv_index", type=str, help="The dataset of segmented pieces of music to use "
                                                     "when the pitch vector algorithm is being used")

    parser.add_argument("--pv_veclength", type=int, default=16,
                        help="The size of the projection vectors used for the locality sensitive hashing algorithm "
                             "(default: %(default)s)")

    parser.add_argument("--list_indexes", action="store_true", default=False,
                        help="If present, dont' run the server but instead list "
                             "the indexes available for the graph and pitch vector algorithm")
    args = parser.parse_args()

    if args.list_indexes:
        print(f"--list_indexes specified.")
        print(f"Available graph indexes:")

        ls_output_graph = pathlib.Path("mid/generated/graph").iterdir()
        for file_folder in ls_output_graph:
            if file_folder.is_dir():
                print(f"\t{file_folder.name}")

        print(f"Available pitch vector indexes:")
        ls_output_vector = pathlib.Path("mid/generated/pitch_vector").iterdir()
        for file_folder in ls_output_vector:
            if file_folder.is_dir():
                print(f"\t{file_folder.name}")
    else:
        if args.pv_dataset is None and args.graph_dataset is None:
            sys.stderr.write("error: at least one index needs to be specified: run python server.py -h "
                             "for more info\n")
            sys.stderr.flush()
            sys.exit(1)
        else:
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
            query_handler_pb2_grpc.add_QueryHandlerServicer_to_server(
                QueryServicer(args.graph_dataset, args.pv_dataset, args.pv_veclength), server)
            server.add_insecure_port('[::]:8007')  # ipv6
            server.start()
            server.wait_for_termination()
