import grpc
from concurrent import futures
from urllib.parse import urlparse
import sys


import A2_pb2
import A2_pb2_grpc

MAXSERVERS = 5
SERVERS = set()
primaryServer = None

class RegistryServerServicer(A2_pb2_grpc.RegistryServerServicer):
    def RegisterServer(self, request, context):
        print(f'JOIN REQUEST FROM {request.ip}:{request.port}')
        
        if len(SERVERS) == MAXSERVERS:
            print("MAX CONNECTION LIMIT REACHED, REJECTING THE REQUEST FOR REGISTRATION")
            return A2_pb2.ServerDetails(ip="", port="")
        
        else:
            server = (request.ip, request.port)
            SERVERS.add(server)
            
            global primaryServer
            if primaryServer == None:
                primaryServer = server

            # Send joining info to the primary server
            with grpc.insecure_channel(f'{primaryServer[0]}:{primaryServer[1]}') as channel:
                stub = A2_pb2_grpc.ServerStub(channel)
                request = A2_pb2.ServerDetails(ip=server[0], port=server[1])
                stub.SendJoiningInfo(request)
            
            # Return the primary server's details
            return A2_pb2.ServerDetails(ip = primaryServer[0], port = primaryServer[1])

    def GetServerList(self, request, context):
        client_address = urlparse(context.peer()).path
        idx = client_address.rfind(':')
        ip = client_address[:idx]
        port = client_address[idx+ 1:]
        print(f'SERVER LIST REQUEST FROM {ip}:{port}')
        return A2_pb2.ServerList(servers=[A2_pb2.ServerDetails(ip=ip, port=port) for ip, port in SERVERS])


def serve(host, port):
    registryServer = grpc.server(futures.ThreadPoolExecutor(max_workers=MAXSERVERS))
    A2_pb2_grpc.add_RegistryServerServicer_to_server(RegistryServerServicer(), registryServer)
    registryServer.add_insecure_port(f"{host}:{port}")
    registryServer.start();
    registryServer.wait_for_termination()

if __name__ == "__main__":
    serve(host="localhost", port=6000)