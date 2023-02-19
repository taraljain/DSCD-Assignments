import grpc
from concurrent import futures
import A1_pb2
import A1_pb2_grpc
from urllib.parse import urlparse
from datetime import date, datetime

MAXCLIENTS = 10

CLIENTELES = set()

ARTICLES = []

AVAILABLESERVERS = set()
CONNECTEDSERVERS = set()

class ServerServicer(A1_pb2_grpc.ServerServicer):
    def JoinServer(self, request, context):
        CLIENT_UUID = request.UUID
        print(f'JOIN REQUEST FROM {CLIENT_UUID}')
        
        if len(CLIENTELES) == MAXCLIENTS:
            print("MAX CONNECTION LIMIT REACHED, REJECTING THE REQUEST FOR JOINING")
            return A1_pb2.Status(currentStatus = False)
        
        else:
            if CLIENT_UUID in CLIENTELES:
                return A1_pb2.Status(currentStatus = False)
            else:
                CLIENTELES.add(CLIENT_UUID)
                return A1_pb2.Status(currentStatus = True)
    
    def LeaveServer(self, request, context):
        CLIENT_UUID = request.UUID
        print(f'LEAVE REQUEST FROM {CLIENT_UUID}')

        if CLIENT_UUID in CLIENTELES:
            CLIENTELES.remove(CLIENT_UUID)
            return A1_pb2.Status(currentStatus = True)
        
        else:
            return A1_pb2.Status(currentStatus = False)

    def GetArticles(self, request, context):
        CLIENT_UUID = request.user.UUID
        print(f'ARTICLES REQUEST FROM {CLIENT_UUID}')
        connectedArticles = GetConnectedArticles()
        date_format = "%d/%m/%Y"
        date_requested = datetime.strptime(request.date, date_format)
        toReturn = []

        allArticles = ARTICLES + connectedArticles

        if CLIENT_UUID in CLIENTELES:
            for article in allArticles:
                date_article = datetime.strptime(article[3], "%d/%m/%Y")
                diff = date_requested - date_article
                if ((request.type == article[0] or request.type == A1_pb2.Type.NONE) and (request.author == article[1] or request.author == "") and diff.days <= 0):
                    toReturn.append(A1_pb2.Article(type=article[0], author=article[1], content=article[2], date=article[3]))
            
        return A1_pb2.ArticlesList(articles=toReturn)
    
    def GetAllArticles(self, request, context):
        toReturn = []
        for article in ARTICLES:
            toReturn.append(A1_pb2.Article(type=article[0], author=article[1], content=article[2], date=article[3]))
        return A1_pb2.ArticlesList(articles=toReturn)

    def PublishArticle(self, request, context):
        CLIENT_UUID = request.user.UUID
        
        if CLIENT_UUID in CLIENTELES:
            print(f'ARTICLE PUBLISHED FROM {CLIENT_UUID}')
            ARTICLES.append((request.type, request.author, request.content, date.today().strftime("%d/%m/%Y")))
            return A1_pb2.Status(currentStatus = True)
        else:
            return A1_pb2.Status(currentStatus = False)


def registerSelf(name, host, port):
    with grpc.insecure_channel('localhost:6000') as channel:
        stub = A1_pb2_grpc.RegistryServerStub(channel)
        request = A1_pb2.ServerDetails(name=name , ip=host, port=port)
        success = stub.RegisterServer(request)
        return success.currentStatus
        
def fillConnectedServersList():
    AVAILABLESERVERS.clear()
    with grpc.insecure_channel('localhost:6000') as channel:
        stub = A1_pb2_grpc.RegistryServerStub(channel)
        
        serversList = stub.GetServerList(A1_pb2.Empty()).servers

        print("Here is the list of active servers:")

        for idx, address in enumerate(serversList):
            print("{}. Name = {}, IP = {}, Port = {}".format(idx + 1, address.name, address.ip, address.port))
            AVAILABLESERVERS.add((address.ip, address.port))

        while True:
            serverIndex = int(input("Please enter to which you want to connect\n"))
            
            if serverIndex > 0 and serverIndex <= len(AVAILABLESERVERS):
                CONNECTEDSERVERS.add(list(AVAILABLESERVERS)[serverIndex - 1])
            else:
                print('Please enter the correct value\n')
                fillConnectedServersList()
                
def GetConnectedArticles():
    toReturn = []
    for server in CONNECTEDSERVERS:
        with grpc.insecure_channel(f'{server[0]}:{server[1]}') as channel:
            stub = A1_pb2_grpc.ServerStub(channel)
            articlesList = stub.GetAllArticles(A1_pb2.Empty()).articles
            for article in articlesList:
                toReturn.append((article.type, article.author, article.content, article.date))

    return toReturn

def serve(host, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAXCLIENTS))
    A1_pb2_grpc.add_ServerServicer_to_server(ServerServicer(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    return server

if __name__ == "__main__":
    name = "Server_1"
    host="localhost"
    port="5000"
    if registerSelf(name, host, port):
        print('Server Registered')
        server = serve(host, port)
        print('server started')
        fillConnectedServersList()
        server.wait_for_termination()
    else:
        print("Registration Failed..!!")