import A2_pb2 
import A2_pb2_grpc
import grpc
from concurrent import futures
import sys
import random
import datetime
import queue
import threading
import os
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

        if check_file_exists(key,fileName):
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
        key=request.UUID
        fileName=f"{port}/{request.name}.txt"

        if check_file_exists(key,fileName):
            request_uuid=request.UUID
            request_name=request.name
            request_content=request.content

            response_val=[None]*1

            t1=threading.Thread(target=WritePrimaryHelper,args=(request_uuid,request_name,request_content,response_val))
            t2=threading.Thread(target=WriteBackupRelicas,args=(request_uuid,request_name,request_content))
            
            t1.start()
            t2.start()
            
            return response_val[0]

        elif request.UUID not in DataStore and os.path.isfile(f'{port}/{request.name}.txt'):
            return A2_pb2.WriteResponse(status="FILE WITH THE SAME NAME ALREADY EXISTS", UUID="" ,version="")
        elif request.UUID not in DataStore and not os.path.isfile(f'{port}/{request.name}.txt'):
            return A2_pb2.WriteResponse(status="DELETED FILE CANNOT BE UPDATED", UUID="" ,version="")


    def WriteServer(self, request, context):
        print("Write request received by replica server")
        key=request.UUID
        fileName=f"{port}/{request.name}.txt"

        if check_file_exists(key,fileName):
            DataStore.update({request.UUID: (request.name, request.version)})

            # Save request.content to the file system
            saveFile(port, f'{request.name}.txt', request.content)

            return A2_pb2.Response(status="SUCCESS")
        
        elif request.UUID not in DataStore and os.path.isfile(f'{port}/{request.name}.txt'):
            return A2_pb2.WriteResponse(status="FILE WITH THE SAME NAME ALREADY EXISTS", UUID="" ,version="")
        elif request.UUID not in DataStore and not os.path.isfile(f'{port}/{request.name}.txt'):
            return A2_pb2.WriteResponse(status="DELETED FILE CANNOT BE UPDATED", UUID="" ,version="")

    def Delete(self, request, context):
        return super().Delete(request, context)
    
    
    def DeletePrimary(self, request, context):
        return super().DeletePrimary(request, context)
    

    def DeleteServer(self, request, context):
        return super().DeleteServer(request, context)


# write to primary replica only
def WritePrimaryHelper(request_UUID,request_name,request_content,response_val):
        current_time = str(datetime.datetime.now())
        DataStore.update({request_UUID:{request_name,current_time}})

        saveFile(port,f'{request_name}.txt',request_content)

        response_val[0]=A2_pb2.WriteResponse(status="SUCCESS", UUID=request_UUID ,version=current_time)

    # send write request to backup replicas
def WriteBackupRelicas(request_UUID,request_name,request_content):
        current_time = str(datetime.datetime.now())
        # Create a queue to communicate with replica threads
        q = queue.Queue()

        def sendWriteRequestToServers(server):
            with grpc.insecure_channel(f'{server[0]}:{server[1]}') as channel:
                stub = A2_pb2_grpc.ServerStub(channel)
                req = A2_pb2.WriteRequestServer(name=request_name, content=request_content, UUID=request_UUID, version=current_time)
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
            print("Write request to all backup replicas completed successfully ...")
        else:
            print("Write request to some backup replicas failed ...")

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

def check_file_exists(key,fileName):
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
    
