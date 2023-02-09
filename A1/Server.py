import grpc
from concurrent import futures
import A1_pb2
import A1_pb2_grpc
from urllib.parse import urlparse
from datetime import date, datetime

MAXCLIENTS = 10

CLIENTELES = set()

ARTICLES = []

class ServerServicer(A1_pb2_grpc.ServerServicer):
    def JoinServer(self, request, context):
        print("Joining Request Received")
        
        if len(CLIENTELES) == MAXCLIENTS:
            print("MAX CONNECTION LIMIT REACHED, REJECTING THE REQUEST FOR JOINING")
            return A1_pb2.Status(currentStatus = False)
        
        else:
            client_address = urlparse(context.peer()).path
            ip = client_address[:client_address.rfind(':')]
            
            if ip in CLIENTELES:
                return A1_pb2.Status(currentStatus = False)
            else:
                CLIENTELES.add(ip)
                print(CLIENTELES)
                return A1_pb2.Status(currentStatus = True)
    
    def LeaveServer(self, request, context):
        client_address = urlparse(context.peer()).path
        ip = client_address[:client_address.rfind(':')]
        
        if ip in CLIENTELES:
            CLIENTELES.remove(ip)
            return A1_pb2.Status(currentStatus = True)
        
        else:
            return A1_pb2.Status(currentStatus = False)

    def GetArticles(self, request, context):
        client_address = urlparse(context.peer()).path
        ip = client_address[:client_address.rfind(':')]
        date_format = "%d/%m/%Y"
        date_requested = datetime.strptime(request.date, date_format)
        toReturn = []

        if ip in CLIENTELES:
            for article in ARTICLES:
                date_article = datetime.strptime(article[3], "%d/%m/%Y")
                diff = date_requested - date_article
                if ((request.type == article[0] or request.type == "") and (request.author == article[1] or request.type == " ") and diff.days <= 0):
                    toReturn.append(A1_pb2.Article(type=article[0], author=article[1], content=article[2], date=article[3]))
            
        return A1_pb2.ArticlesList(articles=toReturn)

    def PublishArticle(self, request, context):
        client_address = urlparse(context.peer()).path
        ip = client_address[:client_address.rfind(':')]
        
        if ip in CLIENTELES:
            ARTICLES.append((request.type, request.author, request.content, date.today().strftime("%d/%m/%Y")))
            return A1_pb2.Status(currentStatus = True)
        else:
            return A1_pb2.Status(currentStatus = False)


def registerSelf(host, port):
    with grpc.insecure_channel('localhost:6000') as channel:
        stub = A1_pb2_grpc.RegistryServerStub(channel)
        request = A1_pb2.Address(ip=host, port=port)
        success = stub.RegisterServer(request)
        return success.currentStatus
        

def serve(host, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAXCLIENTS))
    A1_pb2_grpc.add_ServerServicer_to_server(ServerServicer(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    host="localhost"
    port="5000"
    if registerSelf(host, port):
        print('Server Registered')
        serve(host, port)
    else:
        print("Registration Failed..!!")