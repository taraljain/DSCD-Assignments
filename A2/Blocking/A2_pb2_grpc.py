# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import A2_pb2 as A2__pb2


class RegistryServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RegisterServer = channel.unary_unary(
                '/RegistryServer/RegisterServer',
                request_serializer=A2__pb2.ServerDetails.SerializeToString,
                response_deserializer=A2__pb2.ServerDetails.FromString,
                )
        self.GetServerList = channel.unary_unary(
                '/RegistryServer/GetServerList',
                request_serializer=A2__pb2.Empty.SerializeToString,
                response_deserializer=A2__pb2.ServerList.FromString,
                )


class RegistryServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RegisterServer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetServerList(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RegistryServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RegisterServer': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterServer,
                    request_deserializer=A2__pb2.ServerDetails.FromString,
                    response_serializer=A2__pb2.ServerDetails.SerializeToString,
            ),
            'GetServerList': grpc.unary_unary_rpc_method_handler(
                    servicer.GetServerList,
                    request_deserializer=A2__pb2.Empty.FromString,
                    response_serializer=A2__pb2.ServerList.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'RegistryServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RegistryServer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RegisterServer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RegistryServer/RegisterServer',
            A2__pb2.ServerDetails.SerializeToString,
            A2__pb2.ServerDetails.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetServerList(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RegistryServer/GetServerList',
            A2__pb2.Empty.SerializeToString,
            A2__pb2.ServerList.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class ServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendJoiningInfo = channel.unary_unary(
                '/Server/SendJoiningInfo',
                request_serializer=A2__pb2.ServerDetails.SerializeToString,
                response_deserializer=A2__pb2.Empty.FromString,
                )
        self.Write = channel.unary_unary(
                '/Server/Write',
                request_serializer=A2__pb2.WriteRequest.SerializeToString,
                response_deserializer=A2__pb2.WriteResponse.FromString,
                )
        self.WritePrimary = channel.unary_unary(
                '/Server/WritePrimary',
                request_serializer=A2__pb2.WriteRequest.SerializeToString,
                response_deserializer=A2__pb2.WriteResponse.FromString,
                )
        self.WriteServer = channel.unary_unary(
                '/Server/WriteServer',
                request_serializer=A2__pb2.WriteRequestServer.SerializeToString,
                response_deserializer=A2__pb2.Response.FromString,
                )
        self.Read = channel.unary_unary(
                '/Server/Read',
                request_serializer=A2__pb2.RDRequest.SerializeToString,
                response_deserializer=A2__pb2.ReadResponse.FromString,
                )
        self.Delete = channel.unary_unary(
                '/Server/Delete',
                request_serializer=A2__pb2.RDRequest.SerializeToString,
                response_deserializer=A2__pb2.Response.FromString,
                )
        self.DeletePrimary = channel.unary_unary(
                '/Server/DeletePrimary',
                request_serializer=A2__pb2.RDRequest.SerializeToString,
                response_deserializer=A2__pb2.Response.FromString,
                )
        self.DeleteServer = channel.unary_unary(
                '/Server/DeleteServer',
                request_serializer=A2__pb2.DeleteRequestServer.SerializeToString,
                response_deserializer=A2__pb2.Response.FromString,
                )


class ServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendJoiningInfo(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Write(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WritePrimary(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WriteServer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Read(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeletePrimary(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteServer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendJoiningInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.SendJoiningInfo,
                    request_deserializer=A2__pb2.ServerDetails.FromString,
                    response_serializer=A2__pb2.Empty.SerializeToString,
            ),
            'Write': grpc.unary_unary_rpc_method_handler(
                    servicer.Write,
                    request_deserializer=A2__pb2.WriteRequest.FromString,
                    response_serializer=A2__pb2.WriteResponse.SerializeToString,
            ),
            'WritePrimary': grpc.unary_unary_rpc_method_handler(
                    servicer.WritePrimary,
                    request_deserializer=A2__pb2.WriteRequest.FromString,
                    response_serializer=A2__pb2.WriteResponse.SerializeToString,
            ),
            'WriteServer': grpc.unary_unary_rpc_method_handler(
                    servicer.WriteServer,
                    request_deserializer=A2__pb2.WriteRequestServer.FromString,
                    response_serializer=A2__pb2.Response.SerializeToString,
            ),
            'Read': grpc.unary_unary_rpc_method_handler(
                    servicer.Read,
                    request_deserializer=A2__pb2.RDRequest.FromString,
                    response_serializer=A2__pb2.ReadResponse.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=A2__pb2.RDRequest.FromString,
                    response_serializer=A2__pb2.Response.SerializeToString,
            ),
            'DeletePrimary': grpc.unary_unary_rpc_method_handler(
                    servicer.DeletePrimary,
                    request_deserializer=A2__pb2.RDRequest.FromString,
                    response_serializer=A2__pb2.Response.SerializeToString,
            ),
            'DeleteServer': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteServer,
                    request_deserializer=A2__pb2.DeleteRequestServer.FromString,
                    response_serializer=A2__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Server', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Server(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendJoiningInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Server/SendJoiningInfo',
            A2__pb2.ServerDetails.SerializeToString,
            A2__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Write(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Server/Write',
            A2__pb2.WriteRequest.SerializeToString,
            A2__pb2.WriteResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def WritePrimary(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Server/WritePrimary',
            A2__pb2.WriteRequest.SerializeToString,
            A2__pb2.WriteResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def WriteServer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Server/WriteServer',
            A2__pb2.WriteRequestServer.SerializeToString,
            A2__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Read(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Server/Read',
            A2__pb2.RDRequest.SerializeToString,
            A2__pb2.ReadResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Delete(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Server/Delete',
            A2__pb2.RDRequest.SerializeToString,
            A2__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeletePrimary(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Server/DeletePrimary',
            A2__pb2.RDRequest.SerializeToString,
            A2__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteServer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Server/DeleteServer',
            A2__pb2.DeleteRequestServer.SerializeToString,
            A2__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
