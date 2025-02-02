# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import realtime_rec.protobuf.rank_engine_pb2 as rank__engine__pb2


class RankEngineStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RankRequest = channel.unary_unary(
                '/rankengine.RankEngine/RankRequest',
                request_serializer=rank__engine__pb2.RequestInfo.SerializeToString,
                response_deserializer=rank__engine__pb2.Response.FromString,
                )
        self.UpdateModel = channel.unary_unary(
                '/rankengine.RankEngine/UpdateModel',
                request_serializer=rank__engine__pb2.UpdateRequestInfo.SerializeToString,
                response_deserializer=rank__engine__pb2.Response.FromString,
                )


class RankEngineServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RankRequest(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateModel(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RankEngineServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RankRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.RankRequest,
                    request_deserializer=rank__engine__pb2.RequestInfo.FromString,
                    response_serializer=rank__engine__pb2.Response.SerializeToString,
            ),
            'UpdateModel': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateModel,
                    request_deserializer=rank__engine__pb2.UpdateRequestInfo.FromString,
                    response_serializer=rank__engine__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'rankengine.RankEngine', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RankEngine(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RankRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/rankengine.RankEngine/RankRequest',
            rank__engine__pb2.RequestInfo.SerializeToString,
            rank__engine__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateModel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/rankengine.RankEngine/UpdateModel',
            rank__engine__pb2.UpdateRequestInfo.SerializeToString,
            rank__engine__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
