# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from AutoRecall.proto import merge_pb2 as AutoRecall_dot_proto_dot_merge__pb2


class MergeServiceStub(object):
    """rpc 服务
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.DoMerge = channel.unary_unary(
                '/proto.MergeService/DoMerge',
                request_serializer=AutoRecall_dot_proto_dot_merge__pb2.MergeRequest.SerializeToString,
                response_deserializer=AutoRecall_dot_proto_dot_merge__pb2.MergeResponse.FromString,
                )


class MergeServiceServicer(object):
    """rpc 服务
    """

    def DoMerge(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MergeServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'DoMerge': grpc.unary_unary_rpc_method_handler(
                    servicer.DoMerge,
                    request_deserializer=AutoRecall_dot_proto_dot_merge__pb2.MergeRequest.FromString,
                    response_serializer=AutoRecall_dot_proto_dot_merge__pb2.MergeResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'proto.MergeService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MergeService(object):
    """rpc 服务
    """

    @staticmethod
    def DoMerge(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/proto.MergeService/DoMerge',
            AutoRecall_dot_proto_dot_merge__pb2.MergeRequest.SerializeToString,
            AutoRecall_dot_proto_dot_merge__pb2.MergeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
