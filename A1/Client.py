import grpc
import A1_pb2
import A1_pb2_grpc

SERVERS = set()

def getServersAddress():
    while True:
        serverIndex = int(input("Please enter to which you want to connect\n"))
        
        if serverIndex > 0 and serverIndex <= len(SERVERS):
            return list(SERVERS)[serverIndex - 1]
        else:
            print('Please enter the correct value\n')


def getActiveServersList():
    with grpc.insecure_channel('localhost:6000') as channel:
        stub = A1_pb2_grpc.RegistryServerStub(channel)
        
        serversList = stub.GetServerList(A1_pb2.Empty()).servers

        print("Here is the list of active servers:")

        for idx, address in enumerate(serversList):
            print("Server {}: IP = {}, Port = {}".format(idx + 1, address.ip, address.port))
            SERVERS.add((address.ip, address.port))

def joinServer():
    ip, port = getServersAddress()
    with grpc.insecure_channel(f'{ip}:{port}') as channel:
        stub = A1_pb2_grpc.ServerStub(channel)
        request = A1_pb2.Empty()
        success = stub.JoinServer(request)
        return success.currentStatus


def leaveServer():
    ip, port = getServersAddress()
    with grpc.insecure_channel(f'{ip}:{port}') as channel:
        stub = A1_pb2_grpc.ServerStub(channel)
        request = A1_pb2.Empty()
        success = stub.LeaveServer(request)
        return success.currentStatus

def publishArticle():
    ip, port = getServersAddress()
    
    idx = int(input("""
    Enter the type of Article
    [1] Sport
    [2] Fashion
    [3] Politics\n"""))

    if idx == 1:
        type = A1_pb2.Type.SPORT
    elif idx == 2:
        type = A1_pb2.Type.FASHION
    else:
        type = A1_pb2.Type.POLITICS

    author = input("Enter the Author's Name\n")
    context = input("Enter the content in NOT more than 200 words\n")

    with grpc.insecure_channel(f'{ip}:{port}') as channel:
        stub = A1_pb2_grpc.ServerStub(channel)
        request = A1_pb2.Article(type=type, author=author, content=context, date="")
        success = stub.PublishArticle(request)
        return success.currentStatus

def getArticles():
    ip, port = getServersAddress()
    with grpc.insecure_channel(f'{ip}:{port}') as channel:
        stub = A1_pb2_grpc.ServerStub(channel)
        request = A1_pb2.ArticleRequest(type=A1_pb2.Type.SPORT, author="Taral Jain", date="01/01/2022")
        articlesList = stub.GetArticles(request)
        return articlesList

def run():
    while True:
        OPERATION = int(input("""
    What you want to do?
    1. Get active servers list
    2. Join a Server
    3. Leave a Server
    4. Get the Articles
    5. Publish an Article
    6. Stop the Client\n
    """))
        if OPERATION == 1:
            getActiveServersList()
        elif OPERATION == 2:
            print(joinServer())
        elif OPERATION == 3:
            print(leaveServer())
        elif OPERATION == 4:
            print(getArticles())
        elif OPERATION == 5:
            print(publishArticle())
        elif OPERATION == 6:
            print("Signing off, Thank You..!!")
            return


if __name__ == "__main__":
    run()