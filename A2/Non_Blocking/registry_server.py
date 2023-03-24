import A2_pb2 
import A2_pb2_grpc
import grpc
from concurrent import futures
from urllib.parse import urlparse
MAXSERVERS = 5
servers=set()
primaryServer=None


class RegistryServerServicer(A2_pb2_grpc.RegistryServerServicer):
    def RegisterServer(self, request, context):
        request_ip=request.ip
        request_port=request.port

        print(f"JOIN REQUEST FROM {request_ip}:{request_port}")

        # if max server limit is reached
        if len(servers)==MAXSERVERS:
            print("MAX CONNECTION LIMIT REACHED, REJECTING THE REQUEST FOR REGISTRATION")
            return A2_pb2.ServerDetails(ip="", port="")

        new_server=(request_ip,request_port)
        servers.add(new_server)
        
        global primaryServer
        
        # if primaryServer is none, declare current server as primary server
        if primaryServer==None:
            primaryServer=new_server
        

        with grpc.insecure_channel(f"{primaryServer[0]}:{primaryServer[1]}") as channel:
            server_stub=A2_pb2_grpc.ServerStub(channel)
            request=A2_pb2.ServerDetails(ip=request_ip,port=request_port)
            server_stub.SendJoiningInfo(request)

        # return the primary server details
        return A2_pb2.ServerDetails(ip = primaryServer[0], port = primaryServer[1])


    def GetServerList(self, request, context):
        client_address = urlparse(context.peer()).path
        idx = client_address.rfind(':')
        ip = client_address[:idx]
        port = client_address[idx+ 1:]
        print(f'SERVER LIST REQUEST FROM {ip}:{port}')

        return A2_pb2.ServerList(servers=[A2_pb2.ServerDetails(ip=ip, port=port) for ip, port in servers])
    

def start(host,port):
    registryServer=grpc.server(futures.ThreadPoolExecutor(max_workers=MAXSERVERS))
    A2_pb2_grpc.add_RegistryServerServicer_to_server(RegistryServerServicer(),registryServer)
    registryServer.add_insecure_port(f"{host}:{port}")
    registryServer.start()
    registryServer.wait_for_termination()


if __name__=='__main__':
    start(host='localhost',port='6000')