# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import realtime_rec.protobuf.offline_engine_pb2 as offline__engine__pb2


class OfflineEngineStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RankSampleMakerRequest = channel.unary_unary(
                '/offline_engine.OfflineEngine/RankSampleMakerRequest',
                request_serializer=offline__engine__pb2.RankSampleMakerRequestInfo.SerializeToString,
                response_deserializer=offline__engine__pb2.Response.FromString,
                )
        self.RankTrainerRequest = channel.unary_unary(
                '/offline_engine.OfflineEngine/RankTrainerRequest',
                request_serializer=offline__engine__pb2.RankTrainerRequestInfo.SerializeToString,
                response_deserializer=offline__engine__pb2.Response.FromString,
                )
        self.RecallSampleMakerRequest = channel.unary_unary(
                '/offline_engine.OfflineEngine/RecallSampleMakerRequest',
                request_serializer=offline__engine__pb2.RecallSampleMakerRequestInfo.SerializeToString,
                response_deserializer=offline__engine__pb2.Response.FromString,
                )
        self.RecallTrainerRequest = channel.unary_unary(
                '/offline_engine.OfflineEngine/RecallTrainerRequest',
                request_serializer=offline__engine__pb2.RecallTrainerRequestInfo.SerializeToString,
                response_deserializer=offline__engine__pb2.Response.FromString,
                )


class OfflineEngineServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RankSampleMakerRequest(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RankTrainerRequest(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RecallSampleMakerRequest(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RecallTrainerRequest(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OfflineEngineServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RankSampleMakerRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.RankSampleMakerRequest,
                    request_deserializer=offline__engine__pb2.RankSampleMakerRequestInfo.FromString,
                    response_serializer=offline__engine__pb2.Response.SerializeToString,
            ),
            'RankTrainerRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.RankTrainerRequest,
                    request_deserializer=offline__engine__pb2.RankTrainerRequestInfo.FromString,
                    response_serializer=offline__engine__pb2.Response.SerializeToString,
            ),
            'RecallSampleMakerRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.RecallSampleMakerRequest,
                    request_deserializer=offline__engine__pb2.RecallSampleMakerRequestInfo.FromString,
                    response_serializer=offline__engine__pb2.Response.SerializeToString,
            ),
            'RecallTrainerRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.RecallTrainerRequest,
                    request_deserializer=offline__engine__pb2.RecallTrainerRequestInfo.FromString,
                    response_serializer=offline__engine__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'offline_engine.OfflineEngine', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class OfflineEngine(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RankSampleMakerRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/offline_engine.OfflineEngine/RankSampleMakerRequest',
            offline__engine__pb2.RankSampleMakerRequestInfo.SerializeToString,
            offline__engine__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RankTrainerRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/offline_engine.OfflineEngine/RankTrainerRequest',
            offline__engine__pb2.RankTrainerRequestInfo.SerializeToString,
            offline__engine__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RecallSampleMakerRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/offline_engine.OfflineEngine/RecallSampleMakerRequest',
            offline__engine__pb2.RecallSampleMakerRequestInfo.SerializeToString,
            offline__engine__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RecallTrainerRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/offline_engine.OfflineEngine/RecallTrainerRequest',
            offline__engine__pb2.RecallTrainerRequestInfo.SerializeToString,
            offline__engine__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
