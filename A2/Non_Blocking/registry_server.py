import A2_pb2 
import A2_pb2_grpc
import grpc
from concurrent import futures
MAXSERVERS = 5

class RegistryServerServicer(A2_pb2_grpc.RegistryServerServicer):
    def RegisterServer(self, request, context):
        return super().RegisterServer(request, context)


    def GetServerList(self, request, context):
        return super().GetServerList(request, context)
    

def start(host,port):
    registryServer=grpc.server(futures.ThreadPoolExecutor(max_workers=MAXSERVERS))
    A2_pb2_grpc.add_RegistryServerServicer_to_server(RegistryServerServicer(),registryServer)
    registryServer.add_insecure_port(f"{host}:{port}")
    registryServer.start()
    registryServer.wait_for_termination()


if __name__=='__main__':
    start(host='localhost',port='6000')