from datetime import date
from helper import REQUEST
import pickle
import zmq
    
class Server:
    registryServerAddr = "tcp://127.0.0.1:8000"
    def __init__(self, maxClients):
        '''
        initializes the server,
        binds it to a random free port
        ''' 
        self.maxClients = maxClients
        self.totalClients = 0
        self.clientele = []
        self.articles = []
        
        self.serverContext = zmq.Context.instance()
        self.server = self.serverContext.socket(zmq.REP)
        port_selected = self.server.bind_to_random_port("tcp://*")
        print("Server running on tcp://127.0.0.1:" + str(port_selected))
        self.serverName = input("Server Name: ")
        self.serverAddr = "tcp://127.0.0.1:" + str(port_selected)
        
    def register(self):
        '''
        parameters:
        registryServerAddr: address of the registry server
        serverContext: server context
        serverAddr: address of the registry server
        
        connects to the registry server,
        sends the registration request to the registry server,
        and return the response
        
        return:
        0: FAILED REGISTRATION
        1: SUCCESSFUL REGISTRATION
        '''
        
        # connect to the registry Server
        reqSocket = self.serverContext.socket(zmq.REQ)
        reqSocket.connect(self.registryServerAddr)
        
        # send the registration request
        message_content = {
            "reqType": REQUEST.Register.value,
            "serverName": self.serverName,
            "serverAddr": self.serverAddr
        }
        pickled_message = pickle.dumps(message_content)
        reqSocket.send(pickled_message)
        
        #  waits for the registry response
        pickledRecvMsg = reqSocket.recv()
        recvMsg = pickle.loads(pickledRecvMsg)
        return recvMsg["status"]
    
    def serve(self):
        '''
        waits for the requests from clients 
        '''

        while True:
            #  waits for the next request from the clients
            pickledRecvMsg = self.server.recv()
            recvMsg = pickle.loads(pickledRecvMsg)
            
            # parse request type, and calls respective functions
            reqType = recvMsg["reqType"]
            if reqType == REQUEST.JoinServer.value:
                self.joinServer(recvMsg)
            elif reqType == REQUEST.LeaveServer.value:
                self.leaveServer(recvMsg)
            elif reqType == REQUEST.GetArticles.value:
                self.getArticles(recvMsg)
            elif reqType == REQUEST.PublishArticle.value:
                self.publishArticle(recvMsg)
                
    def joinServer(self, recvMsg):
        '''
        paramters:
        recvMsg: received message from a client
        
        parse out the recv msg to get the client UUID,
        sends back SUCCESS if total no of clients <= max no of clients,
        and client does not exist in clientele
        
        return:
        STATUS: 0 or 1
        '''
        
        # parsing out server info
        status = 0
        clientUUDI = recvMsg["clientUUID"]
        print("JOIN REQUEST FROM " + str(clientUUDI))
        
        # checking if total count < max count of clients
        if self.totalClients < self.maxClients:
            if not clientUUDI in self.clientele:
                self.clientele.append(clientUUDI)              
                self.totalClients += 1
                status = 1

        # sending the response back to client
        sendMsg = {
            "status": status
        }
        pickledSendMsg = pickle.dumps(sendMsg)
        self.server.send(pickledSendMsg)
    
    def leaveServer(self, recvMsg):
        '''
        paramters:
        recvMsg: received message from a client
        
        parse out the recv msg to get the client UUID,
        and remove the client from clientele if it exists
        
        return:
        STATUS: 0 or 1
        '''
        
        # parsing out server info
        status = 0
        clientUUDI = recvMsg["clientUUID"]
        print("LEAVE REQUEST FROM " + str(clientUUDI))
        
        # checks if the client exists in the clientele
        if clientUUDI in self.clientele:
            self.clientele.remove(clientUUDI)           
            self.totalClients -= 1
            status = 1

        # sending the response back to client
        sendMsg = {
            "status": status
        }
        pickledSendMsg = pickle.dumps(sendMsg)
        self.server.send(pickledSendMsg)
        
    def getArticles(self, recvMsg):
        '''
        paramters:
        recvMsg: received message from a client
        
        parse out the recv msg to get the client UUID,
        checks if the client is part of its clientele,
        and updates the server articles
        
        return:
        STATUS: 0 or 1
        '''

        # parsing out server info
        status = 0
        clientUUDI = recvMsg["clientUUID"]
        articleRequest = recvMsg["articleRequest"]
        filteredArticles = []
        
        # checks if the client exists in the clientele
        if clientUUDI in self.clientele:
            for article in self.articles:
                if articleRequest.satisfy(article):
                    filteredArticles.append(article)
            
            print("ARTICLES REQUEST FROM " + str(clientUUDI) + " FOR", end = " ")
            print(articleRequest)
            status = 1
        
        # sending the response back to client
        sendMsg = {
            "status": status,
            "articles": filteredArticles
        }
        pickledSendMsg = pickle.dumps(sendMsg)
        self.server.send(pickledSendMsg)
        
    def publishArticle(self, recvMsg):
        '''
        paramters:
        recvMsg: received message from a client
        
        parse out the recv msg to get the client UUID,
        checks if the client is part of its clientele,
        and updates the server articles
        
        return:
        STATUS: 0 or 1
        '''

        # parsing out server info
        status = 0
        clientUUDI = recvMsg["clientUUID"]
        article = recvMsg["article"]
        
        # checks if the client exists in the clientele
        if clientUUDI in self.clientele:
            article.time = date.today().strftime("%d/%m/%Y")
            self.articles.append(article)
            print("ARTICLES PUBLISH FROM " + str(clientUUDI))
            status = 1
        
        # sending the response back to client
        sendMsg = {
            "status": status
        }
        pickledSendMsg = pickle.dumps(sendMsg)
        self.server.send(pickledSendMsg)


if __name__ == "__main__":
    # creates an instance for the server
    server = Server(maxClients=2)
    # registers the server
    if server.register():
        # successful registration
        print("Server Registration: SUCCESS")
        server.serve()
    else:
        # registration failed
        print("Server Registration: FAILED")
        server.serverContext.destroy()
