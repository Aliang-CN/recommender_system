import grpc

from rec.protobuf import offline_train_pb2, offline_train_pb2_grpc

_HOST = 'localhost'
_PORT = '19998'


def rank_sample_maker(argv):
    with grpc.insecure_channel("{}:{}".format(_HOST, _PORT)) as channel:
        client = offline_train_pb2_grpc.OfflineEngineStub(channel=channel)
        request_info = offline_train_pb2.RankSampleMakerRequestInfo()
        request_base_info = request_info.request_base_info
        request_base_info.pipeline_id = "1"
        request_base_info.config = ""
        response = client.RankSampleMakerRequest(request_info)
    print(response)
