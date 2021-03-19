import grpc
from project.server.query_handler_pb2_grpc import QueryHandlerStub
from project.server.query_handler_pb2 import VectorArgs
if __name__ == '__main__':
    channel = grpc.insecure_channel('localhost:8007')
    stub = QueryHandlerStub(channel)
    print("Asking server for similarity rankings for mid/ashover8_pv1.mid with notes from track 0")
    response = stub.QueryPitchVector(VectorArgs(query_mid="mid/ashover8_pv1.mid", melody_track=0))
    print("Asking server for similarity rankings for mid/test_midi_2.mid with notes from track 0")
    response2 = stub.QueryPitchVector(VectorArgs(query_mid="mid/test_midi_2.mid", melody_track=0))
    print(f"The time to query (on the servers end) was \n(response 1) {response.query_time}\n"
          f"(response 2) {response2.query_time}")
