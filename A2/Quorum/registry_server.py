from concurrent import futures
import random
from urllib.parse import urlparse

import grpc
import A2_pb2
import A2_pb2_grpc

# Assumptions
'''
(1) There are no failures in the system. That is, once the replicas and registry server start, they are always online. They never fail. 
If any failure happens, then we have to shutdown the entire system and restart the entire system manually. 

(2) The required number of servers (N, N_r and N_w) are already running before any client request arrives at the registry server.

(3) N < thread pool size 
'''

# Registry Server Metadata
replicas = set()
quorum_size = {}


class RegistryServerServicer(A2_pb2_grpc.RegistryServerServicer):
    def GetReadQuorumReplicas(self, request, context):
        '''
        parameters:
        request: empty request  
        context: server side RPC context     
        
        parses out the context to fetch client address,
        returns a list containing the read quorom info
        '''
        global replicas
        global quorum_size
        client_address = urlparse(context.peer()).path
        idx = client_address.rfind(':')
        # ip = client_address[:idx]
        ip = "localhost"
        port = client_address[idx+ 1:]
        print(f"READ QUOROM LIST REQUEST FROM {ip}:{port}")
        # selecting out the N_r replicas randomly
        read_quorum = random.sample(list(replicas), k=quorum_size["N_r"])
        replicas_list = [A2_pb2.ReplicaInfo(ip=ip, port=port) for ip, port in read_quorum]
        return A2_pb2.ReplicasList(replicas=replicas_list)

    def GetReplicas(self, request, context):    
        '''
        parameters:
        request: empty request  
        context: server side RPC context     
        
        parses out the context to fetch client address,
        returns a list containing all the replicas info
        '''
        global replicas
        global quorum_size
        client_address = urlparse(context.peer()).path
        idx = client_address.rfind(':')
        # ip = client_address[:idx]
        ip = "localhost"
        port = client_address[idx+ 1:]
        print(f"REPLICAS LIST REQUEST FROM {ip}:{port}")
        replicas_list = [A2_pb2.ReplicaInfo(ip=ip, port=port) for ip, port in replicas]
        return A2_pb2.ReplicasList(replicas=replicas_list)        

    def GetWriteQuorumReplicas(self, request, context):
        '''
        parameters:
        request: empty request  
        context: server side RPC context     
        
        parses out the context to fetch client address,
        returns a list containing the write quorom info
        '''
        global replicas
        global quorum_size
        client_address = urlparse(context.peer()).path
        idx = client_address.rfind(':')
        # ip = client_address[:idx]
        ip = "localhost"
        port = client_address[idx+ 1:]
        print(f"WRITE QUOROM LIST REQUEST FROM {ip}:{port}")
        # selecting out the N_w replicas randomly
        write_quorum = random.sample(list(replicas), k=quorum_size["N_w"])
        replicas_list = [A2_pb2.ReplicaInfo(ip=ip, port=port) for ip, port in write_quorum]
        return A2_pb2.ReplicasList(replicas=replicas_list)
    
    def RegisterReplica(self, request, context):
        '''
        parameters:
        request: request having the replica info (ip, port on which the replica is aceepting the requests)
        context: server side RPC context            
        
        saves the replica info,
        returns FAILURE/SUCCESS
        '''
        global replicas
        global quorum_size
        print(f"JOIN REQUEST FROM {request.ip}:{request.port}")
        
        if len(replicas) == quorum_size['N']:
            print(f"{quorum_size['N']} replica(s) are already running. REQUEST DENIED!")
            return A2_pb2.Response(status="FAILURE")
            
        replica = (request.ip, request.port)
        replicas.add(replica)
        return A2_pb2.Response(status="SUCCESS")    
    
 
def set_quorum_size():
    '''
    sets the size of read and write quorum,
    checks the following two constraints:
    (1) N_r + N_w > N
    (2) N_w > N/2
    (3) N_r <= N
    (4) N_w <= N
    returns FAILURE if the constraints are not satisfied, otherwise SUCCESS
    '''
    global quorum_size
    N = int(input("N:"))
    N_r = int(input("N_r:"))
    N_w = int(input("N_w:"))
    
    if (N_r + N_w > N) and (N_w > N/2) and N_r <= N and N_w <= N:
        quorum_size["N"] = N
        quorum_size["N_r"] = N_r
        quorum_size["N_w"] = N_w
        return "SUCCESS"
     
    return "FAILURE"

   
def serve(ip, port, max_workers):
    '''
    parameters:
    ip, port: ip, port on which the server will aceept the requests
    max_workers: size of the thread pool to be used by the server to execute RPC handlers
    
    starts the registry server on the specified port,
    sets N_r, N_w and N
    and servers the client requests
    '''
    # creates a server with RegistryServer service on the specified port
    registryServer = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    A2_pb2_grpc.add_RegistryServerServicer_to_server(RegistryServerServicer(), registryServer)
    registryServer.add_insecure_port(f"{ip}:{port}")
    
    # sets N_r, N_w and N
    status = set_quorum_size()
    while status != "SUCCESS":
        print("Constraints are not satisfied!")
        status = set_quorum_size()
    print(f"N: {quorum_size['N']}, N_r: {quorum_size['N_r']}, N_w: {quorum_size['N_w']}")
    
    # starts the server
    registryServer.start()
    print(f"Registry Server running on {ip}:{port}")
    registryServer.wait_for_termination()
    

if __name__ == "__main__":
    # starts the registry server
    serve(ip="localhost", port="8000", max_workers = 10)
