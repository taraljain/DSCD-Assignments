import grpc
from concurrent import futures
import sys
import random
import datetime
import queue
import threading
import os

sys.path.insert(1, "../")

import A2_pb2
import A2_pb2_grpc

MAXCLIENTS = 10
ARTICLES = []
SERVERS = set()
global primaryServer
DataStore = {}

class ServerServicer(A2_pb2_grpc.ServerServicer):
    def SendJoiningInfo(self, request, context):
        print("New Server Joined with IP: {}, Port: {}".format(request.ip, request.port))

        # Add the new server to the list of active servers if it is NOT primary
        if request.ip != ip or request.port != port:
            SERVERS.add((request.ip, request.port))

        return A2_pb2.Empty()

    ''' 
        Steps:
        1. The request is received by the server
        2. The request is forwarded to the primary server
        3. The primary server writes the data to the file
        4. The primary server sends the write request to the all the servers
        5. The servers write the data to the file
        6. The primary server sends the response to the server which received the request
        7. The server sends the response to the client
    '''
    def Write(self, request, context):
        # Forward the request to the primary server
        print("Write request received")
        with grpc.insecure_channel(f'{primaryServer[0]}:{primaryServer[1]}') as channel:
            stub = A2_pb2_grpc.ServerStub(channel)
            response = stub.WritePrimary(request)
            return response

    def WritePrimary(self, request, context):
        print("Write request received by primary server")
        current_time = str(datetime.datetime.now())
        DataStore.update({request.UUID: (request.name, current_time)})

        # Save request.content to the file system
        saveFile("primary", f'{request.name}.txt', request.content)

        # Create a queue to communicate with replica threads
        q = queue.Queue()

        def sendWriteRequestToServers(server):
            with grpc.insecure_channel(f'{server[0]}:{server[1]}') as channel:
                stub = A2_pb2_grpc.ServerStub(channel)
                req = A2_pb2.WriteRequestServer(name=request.name, content=request.content, UUID=request.UUID, version=current_time)
                response = stub.WriteServer(req)
                
                q.put(response)

        threads = [threading.Thread(target=sendWriteRequestToServers, args=(server,)) for server in SERVERS]
        for thread in threads:
            thread.start()

        # Wait for all threads to finish and collect acknowledgements
        responses = []
        for thread in threads:
            thread.join()
            responses.append(q.get())

        # Check if all replicas successfully wrote the data
        success = all(response.status=="SUCCESS" for response in responses)
        
        if success:
            return A2_pb2.WriteResponse(status="SUCCESS", UUID=request.UUID ,version=current_time)
        else:
            return A2_pb2.WriteResponse(status="FAIL", UUID="" ,version="")
        

    def WriteServer(self, request, context):
        print("Write request received by replica server")
        DataStore.update({request.UUID: (request.name, request.version)})

        # Save request.content to the file system
        saveFile(port, f'{request.name}.txt', request.content)

        return A2_pb2.Response(status="SUCCESS")


        
def saveFile(folder, fileName, content):
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, fileName), 'w') as file:
        file.write(content)


def registerSelf(ip, port):
    with grpc.insecure_channel('localhost:6000') as channel:
        stub = A2_pb2_grpc.RegistryServerStub(channel)
        request = A2_pb2.ServerDetails(ip=ip, port=port)
        response = stub.RegisterServer(request)
        global primaryServer
        primaryServer = (response.ip, response.port)

        print("Primary Server's IP: {}, Port: {}".format(response.ip, response.port))
    

def serve(host, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAXCLIENTS))
    A2_pb2_grpc.add_ServerServicer_to_server(ServerServicer(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    return server

if __name__ == "__main__":
    ip="localhost"
    port = str(random.randint(5000, 5999))
    server = serve(ip, port)
    registerSelf(ip, port)
    server.wait_for_termination()
    