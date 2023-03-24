import A2_pb2 
import os
import A2_pb2_grpc
import grpc
from concurrent import futures
import random
MAXCLIENTS = 10
DataStore = {}
SERVERS = set()
global primaryServer


class ServerServicer(A2_pb2_grpc.ServerServicer):
    def SendJoiningInfo(self, request, context):
        print("New Server Joined with IP: {}, Port: {}".format(request.ip, request.port))

        # Add the new server to the list of active servers if it is NOT primary
        if request.ip != ip or request.port != port:
            SERVERS.add((request.ip, request.port))    
    
    def Read(self, request, context):
        if request.UUID not in DataStore:
            return A2_pb2.ReadResponse(status="FILE DOES NOT EXIST", name="", content="", version="")
        elif not os.path.isfile(f'{port}/{DataStore[request.UUID][0]}.txt'):
            return A2_pb2.ReadResponse(status="FILE ALREADY DELETED", name="", content="", version="")
        else:
            with open(f'{port}/{DataStore[request.UUID][0]}.txt', 'r') as file:
                content = file.read()
            return A2_pb2.ReadResponse(status="SUCCESS", name=DataStore[request.UUID][0], content=content, version=DataStore[request.UUID][1])
    
    '''
        Steps:
        1. Request is received by the server
        2. Server forward the request to the primaryServer
        3. Primary Server writes the data to the file
        4. Primary Server sends the confirmation message to the server which received the request
        5. Primary Server sends the write request to all other servers
        6. Servers writes the data to the file 
    '''

    def Write(self, request, context):
        # Forward the request to the primary server
        print("Write request received")

        key=request.UUID
        fileName=f"{port}/{request.name}.txt"

        if send_to_primary_server(key,fileName):
            with grpc.insecure_channel(f'{primaryServer[0]}:{primaryServer[1]}') as channel:
                stub = A2_pb2_grpc.ServerStub(channel)
                response=stub.WritePrimary(request)
                return response
            
        elif key not in DataStore and os.path.isfile(fileName):
            return A2_pb2.WriteResponse(status="FILE WITH THE SAME NAME ALREADY EXISTS", UUID="" ,version="")

        elif key in DataStore and not os.path.isfile(fileName):
            return A2_pb2.WriteResponse(status="DELETED FILE CANNOT BE UPDATED", UUID="" ,version="")
        

    def WritePrimary(self, request, context):
        print("Write request received by primary server")

    

    def WriteServer(self, request, context):
        return super().WriteServer(request, context)

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

def saveFile(folder, fileName, content):
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, fileName), 'w') as file:
        file.write(content)

def send_to_primary_server(key,fileName):
    if key not in DataStore and not os.path.isfile(fileName):
        return True
    
    if key in DataStore and os.path.isfile(fileName):
        return True
    
    return False

def deleteFile(folder, fileName):
    os.remove(os.path.join(folder, fileName))

def registerSelf(ip, port):
    with grpc.insecure_channel('localhost:6000') as channel:
        stub = A2_pb2_grpc.RegistryServerStub(channel)
        request = A2_pb2.ServerDetails(ip=ip, port=port)
        response = stub.RegisterServer(request)
        global primaryServer
        primaryServer = (response.ip, response.port)

        print("Primary Server's IP: {}, Port: {}".format(response.ip, response.port))

if __name__=='__main__':
    ip="localhost"
    port = str(random.randint(5000, 5999))
    server = start(ip, port)
    registerSelf(ip, port)
    server.wait_for_termination()
    
