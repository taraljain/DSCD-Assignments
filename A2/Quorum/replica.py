from concurrent import futures
import datetime
import os
from urllib.parse import urlparse

import grpc
import A2_pb2
import A2_pb2_grpc
    
data_store = {}

class ReplicaServicer(A2_pb2_grpc.ReplicaServicer):
    def Read(self, request, context):
        '''
        parameters:
        request: request having the file uuid
        context: server side RPC context
        
        parses out the context to fetch client address,
        checks the read scenario, and accordingly 
        fetches the text from the local directory,
        returns FAILURE/SUCCESS
        '''
        global data_store
        
        client_address = urlparse(context.peer()).path
        idx = client_address.rfind(':')
        # ip = client_address[:idx]
        ip = "localhost"
        port = client_address[idx+ 1:]
        print(f"READ REQUEST FROM {ip}:{port}")
        
        # getting the file uuid
        key = request.uuid

        # possible read scenarios
        if (key in data_store):
            filename, timestamp = data_store[key]
            if os.path.isfile(filename):
                # scenario 2: reading existing file
                with open(filename, 'r') as file:
                    content = file.read()
                return A2_pb2.ReadResponse(status="SUCCESS", name=filename, content=content, version=timestamp)
            else:
                # scenario 3: reading deleted file
                return A2_pb2.ReadResponse(status="FILE ALREADY DELETED", version=timestamp)
        else:
            # scenario 1: reading non-existing file
            return A2_pb2.ReadResponse(status="FILE DOES NOT EXIST")

    def Write(self, request, context):
        '''
        parameters:
        request: request having the file name, content, uuid
        context: server side RPC context     
        
        parses out the context to fetch client address,
        gets the key-value pair,
        checks the write scenario, and accordingly 
        adds/updates the text file in the in-memory map and its local store,
        returns FAILURE/SUCCESS
        '''
        global data_store
        
        client_address = urlparse(context.peer()).path
        idx = client_address.rfind(':')
        # ip = client_address[:idx]
        ip = "localhost"
        port = client_address[idx+ 1:]
        print(f"WRITE REQUEST FROM {ip}:{port}")
        
        # getting key-value pair
        key = request.uuid
        filename = request.name
        timestamp = str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
        value = (filename, timestamp)

        # possible write scenarios
        if (key in data_store):
            if os.path.isfile(filename):
                # scenario 3: updating existed file
                data_store[key] = value
                with open(filename, 'w') as file:
                    file.write(request.content)
                return A2_pb2.WriteResponse(status="SUCCESS", uuid=key ,version=timestamp)
            else:
                # scenario 4: updating deleted file
                return A2_pb2.WriteResponse(status="DELETED FILE CANNOT BE UPDATED")
        else:
            if os.path.isfile(filename):
                # scenario 2: creating existed file
                return A2_pb2.WriteResponse(status="FILE WITH THE SAME NAME ALREADY EXISTS")
            else:
                # scenario 1: creating new file
                data_store[key] = value
                with open(filename, 'w') as file:
                    file.write(request.content)
                return A2_pb2.WriteResponse(status="SUCCESS", uuid=key ,version=timestamp)
        
    def Delete(self, request, context):
        '''
        parameters:
        request: request having the file name, content, uuid
        context: server side RPC context     
        
        parses out the context to fetch client address,
        gets the key-value pair,
        checks the delete scenario, and accordingly 
        deletes the text file from the local store and updates the entry the in-memory map,
        returns FAILURE/SUCCESS
        '''
        global data_store
        
        client_address = urlparse(context.peer()).path
        idx = client_address.rfind(':')
        # ip = client_address[:idx]
        ip = "localhost"
        port = client_address[idx+ 1:]
        print(f"DELETE REQUEST FROM {ip}:{port}")
        
        # getting key-value pair
        key = request.uuid
        filename = ""
        timestamp = str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"))
        value = (filename, timestamp)
            
        # possible delete scenarios
        if (key in data_store):
            filename, timestamp = data_store[key]
            if os.path.isfile(filename):
                # scenario 2: deleting existing file
                os.remove(filename)
                data_store[key] = value
                return A2_pb2.DeleteResponse(status="SUCCESS")
            else:
                # scenario 3: deleting deleted file
                return A2_pb2.DeleteResponse(status="FILE ALREADY DELETED")
        else:
            # scenario 1: deleting non-existing file
            data_store[key] = value
            return A2_pb2.DeleteResponse(status="SUCCESS")
    
    
def register(ip, port):
    '''
    parameters:
    ip, port: ip, port on which the server is aceepting the requests
    
    registers the server with the registry server, 
    returns 0 (FAILURE)/1 (SUCCESS)
    '''
    with grpc.insecure_channel("localhost:8000") as channel:
        stub = A2_pb2_grpc.RegistryServerStub(channel)
        request = A2_pb2.ReplicaInfo(ip=ip, port=port)        
        response = stub.RegisterReplica(request)
        return response.status    


def serve(ip, max_workers):
    '''
    parameters:
    ip: ip address on which the server will be aceept the requests
    max_workers: size of the thread pool to be used by the server to execute RPC handlers
    
    starts the replica on a random free port,
    registers it with the registry server,
    create a file directory for persisting data,
    and servers the client requests
    '''
    # starts a server with Replica service on the specified port
    replica = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    A2_pb2_grpc.add_ReplicaServicer_to_server(ReplicaServicer(), replica)
    port = str(replica.add_insecure_port(f"{ip}:0"))
    replica.start()
    print(f"Replica running on {ip}:{port}")
   
    # registers the replica with the registry server
    status = register(ip, port)
    if status == "SUCCESS":
        print("Replica registered successfully!")
        
        # creating a file directory for persisting data
        replica_dir =  f"replica_{ip}_{port}"
        if not os.path.exists(replica_dir):
            os.makedirs(replica_dir)
        os.chdir(replica_dir)
        replica.wait_for_termination()
    else:
        print("Replica registration failed!")
    replica.stop(grace=3)    
    

if __name__ == "__main__":
    # starts the server
    replica = serve(ip="localhost", max_workers = 10)
    