import grpc
import uuid
import sys
import random
from colorama import Fore, Style

sys.path.insert(1, "../")
import A2_pb2
import A2_pb2_grpc

SERVERS = set()
FILES = []

def getActiveServersList():
    with grpc.insecure_channel('localhost:6000') as channel:
        stub = A2_pb2_grpc.RegistryServerStub(channel)
        
        serversList = stub.GetServerList(A2_pb2.Empty()).servers

        print("Here is the list of active servers:")

        for idx, address in enumerate(serversList):
            print("{}. IP = {}, Port = {}".format(idx + 1, address.ip, address.port))
            SERVERS.add((address.ip, address.port))

def generateUUID():
    return str(uuid.uuid1())


def getUUID():
    for index, file in enumerate(FILES):
        print(index, file[0], file[1])

    idx = int(input("Select the UUID of the file you want to update: "))
    return FILES[idx][0]


def chooseRandomServer():
    # Randomly select a server from the list of active servers
    return random.choice(list(SERVERS))


def read():
    UUID = getUUID()

    serverIP, serverPort = chooseRandomServer()

    with grpc.insecure_channel(f'{serverIP}:{serverPort}') as channel:
        stub = A2_pb2_grpc.ServerStub(channel)
        request = A2_pb2.RDRequest(UUID=UUID)
        response = stub.Read(request)

        if response.status == "SUCCESS":
            print(Fore.YELLOW + f'File Name: {response.name}' + Style.RESET_ALL)
            print(Fore.YELLOW + f'File Content: {response.content}' + Style.RESET_ALL)
            print(Fore.LIGHTBLACK_EX + f'Version: {response.version}' + Style.RESET_ALL)

        else:
            print(Fore.RED + response.status + Style.RESET_ALL)


def write():
    # Check if the user wants to write into old file or new file
    type = input("Do you want to write into old file or new file? (old/new): [Y/N]")
    
    if type == "Y":
        UUID = getUUID()
    else:
        UUID = generateUUID()

    name = input("Enter the name of the file: ")
    content = input("Enter the content of the file: ")

    serverIP, serverPort = chooseRandomServer()

    with grpc.insecure_channel(f'{serverIP}:{serverPort}') as channel:
        stub = A2_pb2_grpc.ServerStub(channel)
        request = A2_pb2.WriteRequest(name=name, content=content, UUID=UUID)
        response = stub.Write(request)

        if response.status == "SUCCESS":
            print(Fore.GREEN + response.status + Style.RESET_ALL)
            FILES.append([response.UUID, response.version])
        else:
            print(Fore.RED + response.status + Style.RESET_ALL)
    

def delete():
    UUID = getUUID()

    serverIP, serverPort = chooseRandomServer()

    with grpc.insecure_channel(f'{serverIP}:{serverPort}') as channel:
        stub = A2_pb2_grpc.ServerStub(channel)
        request = A2_pb2.RDRequest(UUID=UUID)
        response = stub.Delete(request)

        print(response.status)


def run():
    while True:
        OPERATION = int(input("""
    What you want to do?
    1. Get active servers list
    2. Read
    3. Write
    4. Delete
    [Press Any Other Number Stop Client]\n
    """))
        if OPERATION == 1:
            getActiveServersList()
        elif OPERATION == 2:
            read()
        elif OPERATION == 3:
            write()
        elif OPERATION == 4:
            delete()
        else:
            print("Signing off, Thank You..!!")
            return


if __name__ == "__main__":
    run()