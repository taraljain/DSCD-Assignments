from datetime import datetime
from enum import Enum
from time import sleep
from uuid import uuid1

import grpc
import A2_pb2
import A2_pb2_grpc


# Assumptions
'''
(1) menu input must be an integer
(2) filename can not be empty
(3) Either writing to all the N_w servers will succeed, or all will fail together
'''     
        
class REQUEST(Enum):
    '''
    class to enumerate all the request types
    '''
    Write = 1
    Read = 2
    Delete = 3
    GetReplicas = 4
    Exit = 5
    
    
class Client:
    '''
    client class
    '''
    registry_server_addr = "localhost:8000"
    files = []
    
    def delete(self):
        '''
        requests the registry server for the write quorum (N_w),
        picks out a UUID, send the delete request to all the replicas in N_w,
        returns 0/1 (FAILURE/SUCCESS)
        '''
        # requesting the registry server for the write quorum
        with grpc.insecure_channel(self.registry_server_addr) as channel:
            stub = A2_pb2_grpc.RegistryServerStub(channel)
            write_quorum = stub.GetWriteQuorumReplicas(A2_pb2.Empty()).replicas
        
        # uuid options
        uuid = ""
        while True:
            if len(self.files) == 0:
                print("\nNo files available to delete\n")
                return 0
            else:
                print("Here are the existing files:")
                for idx, file in enumerate(self.files):
                    print(f"{idx+1}. {file['uuid']}:{file['name']}:{file['version']}")
                file_index = int(input("Enter your choice: ")) - 1
                        
                if file_index >= 0 and file_index < len(self.files):
                    uuid = self.files[file_index]['uuid']
                    break
                else:
                    print("\nInvalid Option\n")
        
        # sending a delete request to all the replicas (N_w)
        deleted = 0
        for _, replica in enumerate(write_quorum):
            replica_addr = f"{replica.ip}:{replica.port}"
            print(f"DELETE REQUEST SENT TO {replica.ip}:{replica.port}")
            with grpc.insecure_channel(replica_addr) as channel:
                stub = A2_pb2_grpc.ReplicaStub(channel)
                delete_request = A2_pb2.DeleteRequest(uuid=uuid)  
                response = stub.Delete(delete_request)
                
                print(f"Status: {response.status}")
                print()
                    
                # file deleted successfully
                if response.status == "SUCCESS":
                    deleted = 1
                                    
        # returning delete status              
        return deleted
    
    def get_replicas(self):
        '''
        creates a channel with the registry server,
        and asks it to send all the replicas info,
        then returns a list containing all the replicas info
        '''
        with grpc.insecure_channel(self.registry_server_addr) as channel:
            stub = A2_pb2_grpc.RegistryServerStub(channel)
            replicas = stub.GetReplicas(A2_pb2.Empty()).replicas
            return replicas
    
    def read(self):
        '''
        requests the registry server for the read quorum (N_r),
        picks out a UUID, send the read request to all the replicas in N_r,
        prints the file contents with the latest timestamp,
        returns 0/1 (FAILURE/SUCCESS)
        '''
        # requesting the registry server for the read quorum
        with grpc.insecure_channel(self.registry_server_addr) as channel:
            stub = A2_pb2_grpc.RegistryServerStub(channel)
            read_quorum = stub.GetReadQuorumReplicas(A2_pb2.Empty()).replicas
        
        # uuid options
        uuid = ""
        while True:
            if len(self.files) == 0:
                print("\nNo files available to read\n")
                return 0
            else:
                print("Here are the existing files:")
                for idx, file in enumerate(self.files):
                    print(f"{idx+1}. {file['uuid']}:{file['name']}:{file['version']}")
                file_index = int(input("Enter your choice: ")) - 1
                        
                if file_index >= 0 and file_index < len(self.files):
                    uuid = self.files[file_index]['uuid']
                    break
                else:
                    print("\nInvalid Option\n")
        
        # sending a read request to all the replicas (N_r)
        version = ""
        name = ""
        content = ""
        isDeleted = False
        for _, replica in enumerate(read_quorum):
            replica_addr = f"{replica.ip}:{replica.port}"
            print(f"READ REQUEST SENT TO {replica.ip}:{replica.port}")
            with grpc.insecure_channel(replica_addr) as channel:
                stub = A2_pb2_grpc.ReplicaStub(channel)
                read_request = A2_pb2.ReadRequest(uuid=uuid)  
                response = stub.Read(read_request)
                
                print(f"Status: {response.status}")
                print(f"Name: {response.name}")
                print(f"Version: {response.version}")
                print()
                    
                if response.status == "SUCCESS" or response.status == "FILE ALREADY DELETED":
                    # picking out the file with the latest version
                    if version == "" or \
                        datetime.strptime(version, "%d/%m/%y %H:%M:%S") < datetime.strptime(response.version, "%d/%m/%y %H:%M:%S"):
                        version = response.version
                        name = response.name
                        content = response.content
                        isDeleted = (response.status == "FILE ALREADY DELETED")
                                
        # read failure from all the replicas (N_r) 
        # or the file has already been deleted
        if isDeleted:
            print(f"File has been deleted ({version})")
        if version == "" or isDeleted:
            return 0
        
        print(f"{name} ({version})")
        print(content)                     
        return 1
    
    def read_all(self):
        '''
        picks out a UUID, send the read request to all the replicas,
        prints the file contents with the latest timestamp,
        returns 0/1 (FAILURE/SUCCESS)
        '''
        # requesting the registry server for the replicas
        read_quorum = self.get_replicas()
        
        # uuid options
        uuid = ""
        while True:
            if len(self.files) == 0:
                print("\nNo files available to read\n")
                return 0
            else:
                print("Here are the existing files:")
                for idx, file in enumerate(self.files):
                    print(f"{idx+1}. {file['uuid']}:{file['name']}:{file['version']}")
                file_index = int(input("Enter your choice: ")) - 1
                        
                if file_index >= 0 and file_index < len(self.files):
                    uuid = self.files[file_index]['uuid']
                    break
                else:
                    print("\nInvalid Option\n")
        
        # sending a read request to all the replicas (N_r)
        version = ""
        name = ""
        content = ""
        isDeleted = False
        for _, replica in enumerate(read_quorum):
            replica_addr = f"{replica.ip}:{replica.port}"
            print(f"READ REQUEST SENT TO {replica.ip}:{replica.port}")
            with grpc.insecure_channel(replica_addr) as channel:
                stub = A2_pb2_grpc.ReplicaStub(channel)
                read_request = A2_pb2.ReadRequest(uuid=uuid)  
                response = stub.Read(read_request)
                
                print(f"Status: {response.status}")
                print(f"Name: {response.name}")
                print(f"Version: {response.version}")
                print()
                    
                if response.status == "SUCCESS" or response.status == "FILE ALREADY DELETED":
                    # picking out the file with the latest version
                    if version == "" or \
                        datetime.strptime(version, "%d/%m/%y %H:%M:%S") < datetime.strptime(response.version, "%d/%m/%y %H:%M:%S"):
                        version = response.version
                        name = response.name
                        content = response.content
                        isDeleted = (response.status == "FILE ALREADY DELETED")
                                
        # read failure from all the replicas (N_r) 
        # or the file has already been deleted
        if isDeleted:
            print(f"File has been deleted ({version})")
        if version == "" or isDeleted:
            return 0
        
        print(f"{name} ({version})")
        print(content)                     
        return 1
        
    def write(self):
        '''
        requests the registry server for the write quorum (N_w),
        generates a new UUID in case of new file, and
        uses same UUID in case of a existing file,
        sends the write request to all the replicas in N_w,
        updates the file info in the memory,
        returns 0/1 (FAILURE/SUCCESS)
        '''
        # requesting the registry server for the write quorum
        with grpc.insecure_channel(self.registry_server_addr) as channel:
            stub = A2_pb2_grpc.RegistryServerStub(channel)
            write_quorum = stub.GetWriteQuorumReplicas(A2_pb2.Empty()).replicas
        
        uuid = ""
        name = ""
        file_index = -1
        # write options
        while True:
            print("[1] Creating a new file")
            if len(self.files) != 0:
                print("[2] Updating an existing file")
            write_req = int(input("Enter your choice: "))
            
            if write_req == 1:
                uuid = str(uuid1())
                name = input("Filename: ")
                file_index = len(self.files)
                break
            elif write_req == 2 and len(self.files) != 0:
                # uuid options
                while True:
                    if len(self.files) == 0:
                        print("\nNo replicas available\n")
                    else:
                        print("Here are the existing files:")
                        for idx, file in enumerate(self.files):
                            print(f"{idx+1}. {file['uuid']}:{file['name']}:{file['version']}")
                        file_index = int(input("Enter your choice: ")) - 1
                        
                        if file_index >= 0 and file_index < len(self.files):
                            uuid = self.files[file_index]['uuid']
                            name = self.files[file_index]['name']
                            break
                        else:
                            print("\nInvalid Option\n")
                break
            else:
                print("\nInvalid Option\n")
        
        # new/updated content
        content = input("Please write down the content\n")
        print()
        
        # writing all the replicas (N_w)
        latest_version = ""
        for _, replica in enumerate(write_quorum):
            replica_addr = f"{replica.ip}:{replica.port}"
            print(f"WRITE REQUEST SENT TO {replica.ip}:{replica.port}")
            with grpc.insecure_channel(replica_addr) as channel:
                stub = A2_pb2_grpc.ReplicaStub(channel)
                write_request = A2_pb2.WriteRequest(name=name, content=content, uuid=uuid)  
                response = stub.Write(write_request)
                
                print(f"Status: {response.status}")
                print(f"UUID: {response.uuid}")
                print(f"Version: {response.version}")
                print()
                latest_version = response.version
                if response.status != "SUCCESS":
                    return 0
                
        # saving the files in the memory
        if file_index == len(self.files):
            # new file
            self.files.append({"uuid": uuid, "name": name, "version": latest_version})
        else:
            # existing file
            self.files[file_index] = {"uuid": uuid, "name": name, "version": latest_version}
        return 1

  
def run_test_cases(sleep_timer):
    '''
    automated test cases
    '''  
    # running a client
    client = Client()
    print(f"\nClient is running\n")
    
    # performing write-read ops
    while True:
        op = input()
        if op == "WRITE":
            # performing write operation
            client.write()
            print(f"\nWrite operation completed!\n")
        elif op == "READ":
            # performing read operation on each replica
            client.read_all()
            print(f"\nRead operation completed!\n")
        elif op == "DELETE":
            client.delete()
        else:
            break
        sleep(sleep_timer)
    return 1
    
  
if __name__ == "__main__":
    # creates an instance for the client
    client = Client()
    
    # menu options
    while True:
        print("Welcome!!! Here are your choices:")
        print("[1] Write operation")
        print("[2] Read operation")
        print("[3] Delete operation")
        print("[4] Get all the replicas")
        print("[5] Exit")
        req = int(input("Enter your choice: "))
        
        if req == REQUEST.Write.value:
            write_status = client.write()
            if write_status:
                print("\nWrite Request SUCCESSFUL\n") 
            else:
                print("\nWrite Request FAILED\n") 
                
        elif req == REQUEST.Read.value:
            read_status = client.read()
            if read_status:
                print("\nRead Request SUCCESSFUL\n") 
            else:
                print("\nRead Request FAILED\n") 
                
        elif req == REQUEST.Delete.value:
            delete_status = client.delete()
            if delete_status:
                print("\nDelete Request SUCCESSFUL\n") 
            else:
                print("\nDelete Request FAILED\n") 
        
        elif req == REQUEST.GetReplicas.value:
            replicas = client.get_replicas()
            if len(replicas) == 0:
                print("\nNo replicas available\n")
            else:
                print("\nHere are the active replicas:")
                for idx, replica in enumerate(replicas):
                    print(f"{idx+1}. {replica.ip}:{replica.port}")
                print()
                
        elif req == REQUEST.Exit.value:
            break
        
        else:
            print("\nInvalid Option\n")
