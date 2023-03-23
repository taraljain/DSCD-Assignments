import A2_pb2 
import A2_pb2_grpc
import grpc
from concurrent import futures
import random
MAXCLIENTS = 10

class ServerServicer(A2_pb2_grpc.ServerServicer):
    def SendJoiningInfo(self, request, context):
        return super().SendJoiningInfo(request, context)


    def Write(self, request, context):
        return super().Write(request, context)


    def WritePrimary(self, request, context):
        return super().WritePrimary(request, context)
    

    def WriteServer(self, request, context):
        return super().WriteServer(request, context)
    
    
    def Read(self, request, context):
        return super().Read(request, context)
    

    def Delete(self, request, context):
        return super().Delete(request, context)
    
    
    def DeletePrimary(self, request, context):
        return super().DeletePrimary(request, context)
    

    def DeleteServer(self, request, context):
        return super().DeleteServer(request, context)


def start(host,port):
    server=grpc.server(futures.ThreadPoolExecutor(max_workers=MAXCLIENTS))
    A2_pb2_grpc.add_ServerServicer_to_server(ServerServicer(),server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    return server

def registerSelf(ip,port):
    pass

if __name__=='__main__':
    ip="localhost"
    port = str(random.randint(5000, 5999))
    server = start(ip, port)
    registerSelf(ip, port)
    server.wait_for_termination()
    
