import grpc
from concurrent import futures
import A1_pb2
import A1_pb2_grpc

MAXSERVERS = 5
SERVERS = set()

class RegistryServerServicer(A1_pb2_grpc.RegistryServerServicer):
    def RegisterServer(self, request, context):
        print(f'JOIN REQUEST FROM {request.ip}:{request.port}')
        
        if len(SERVERS) == MAXSERVERS:
            print("MAX CONNECTION LIMIT REACHED, REJECTING THE REQUEST FOR REGISTRATION")
            return A1_pb2.Status(currentStatus = False)
        
        else:
            server = (request.ip, request.port)
            SERVERS.add(server)
            return A1_pb2.Status(currentStatus = True)

    def GetServerList(self, request, context):
        return A1_pb2.ServerList(servers=[A1_pb2.Address(ip=ip, port=port) for ip, port in SERVERS])


def serve(host, port):
    registryServer = grpc.server(futures.ThreadPoolExecutor(max_workers=MAXSERVERS))
    A1_pb2_grpc.add_RegistryServerServicer_to_server(RegistryServerServicer(), registryServer)
    registryServer.add_insecure_port(f"{host}:{port}")
    registryServer.start();
    registryServer.wait_for_termination()

if __name__ == "__main__":
    serve(host="localhost", port=6000)