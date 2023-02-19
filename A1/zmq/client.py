from helper import Article, ArticleRequest, REQUEST
import pickle
import uuid
import zmq
    
class Client:
    registryServerAddr = "tcp://127.0.0.1:8000"
    def __init__(self):
        '''
        initializes the client,
        binds it to a random free port
        '''
        self.client_id = str(uuid.uuid1())
        
        self.clientContext = zmq.Context.instance()
        self.client = self.clientContext.socket(zmq.REQ)
        port_selected = self.client.bind_to_random_port("tcp://*")
        print("Client running on tcp://127.0.0.1:" + str(port_selected))
        self.clientAddr = "tcp://127.0.0.1:" + str(port_selected)
        
        self.servers = {}
        self.activeServers = []

    def getServerList(self):
        '''
        connects with the registry server,
        sends request to get server list,
        updates the list of all active server nodes
        '''
        
        # connects with the registry server
        self.client.connect(self.registryServerAddr)
        
        # send the request
        message_content = {
            "reqType": REQUEST.GetServerList.value,
            "clientAddr": self.clientAddr
        }
        pickled_message = pickle.dumps(message_content)
        self.client.send(pickled_message)
        
        #  waits for the registry response
        pickledRecvMsg = self.client.recv()
        recvMsg = pickle.loads(pickledRecvMsg)
        
        # updates the active server nodes
        self.activeServers = recvMsg["activeServers"]
        
    def joinServer(self, s_no):
        '''
        paramters:
        s_no: index no of the server
        
        connects with the server (s_no),
        sends request to join it,
        saves the socket in case of success,
        disconnects in case of failure,
        returns the response
        
        return:
        0: FAILED TO JOIN
        1: SUCCESS TO JOIN
        '''
        
        # connect to the server
        clientServerSocket = self.clientContext.socket(zmq.REQ)
        clientServerSocket.connect(self.activeServers[s_no].addr)
        
        # send the join request
        message_content = {
            "reqType": REQUEST.JoinServer.value,
            "clientUUID": self.client_id
        }
        pickled_message = pickle.dumps(message_content)
        clientServerSocket.send(pickled_message)
        
        #  waits for the server response
        pickledRecvMsg = clientServerSocket.recv()
        recvMsg = pickle.loads(pickledRecvMsg)
        
        # saves/close the connection
        if recvMsg["status"]:
            self.servers[self.activeServers[s_no].addr] = clientServerSocket
        else:
            clientServerSocket.disconnect(self.activeServers[s_no].addr)
            clientServerSocket.close()
            
        return recvMsg["status"]
    
    def leaveServer(self, s_no):
        '''
        paramters:
        s_no: index no of the server
        
        gets the saved socket for the server,
        sends request to leave it,
        updates the socket list,
        returns the response
        
        return:
        0: FAILED TO LEAVE
        1: SUCCESS TO LEAVE
        '''
        
        # checks whether the client has joined the server 
        if self.activeServers[s_no].addr not in self.servers:
            return 0
        
        # saved client server socket
        clientServerSocket = self.servers[self.activeServers[s_no].addr]
        
        # send the leave request
        message_content = {
            "reqType": REQUEST.LeaveServer.value,
            "clientUUID": self.client_id
        }
        pickled_message = pickle.dumps(message_content)
        clientServerSocket.send(pickled_message)
        
        #  waits for the server response
        pickledRecvMsg = clientServerSocket.recv()
        recvMsg = pickle.loads(pickledRecvMsg)
        
        # close the connection
        if recvMsg["status"]:
            clientServerSocket.disconnect(self.activeServers[s_no].addr)
            clientServerSocket.close()
            self.servers.pop(self.activeServers[s_no].addr)
            
        return recvMsg["status"]
    
    def getArticles(self, s_no, articleRequest):
        '''
        paramters:
        s_no: index no of the server
        articleRequest: articleRequest specifying the article tags
        
        gets the saved socket for the server,
        sends request to get the articles with specified tags,
        and returns the response
        
        return:
        0 in case of FAILURE
        list of articles in case of SUCCESS
        '''
        
        # checks whether the client has joined the server 
        if self.activeServers[s_no].addr not in self.servers:
            return 0
        
        # saved client server socket
        clientServerSocket = self.servers[self.activeServers[s_no].addr]
        
        # send the get request
        message_content = {
            "reqType": REQUEST.GetArticles.value,
            "clientUUID": self.client_id,
            "articleRequest": articleRequest
        }
        pickled_message = pickle.dumps(message_content)
        clientServerSocket.send(pickled_message)
        
        #  waits for the server response
        pickledRecvMsg = clientServerSocket.recv()
        recvMsg = pickle.loads(pickledRecvMsg)
        
        if recvMsg["status"]:
            # success
            return recvMsg["articles"]
        # failure
        return 0
        
        
    def publishArticle(self, s_no, article):
        '''
        paramters:
        s_no: index no of the server
        article: article that the client wants to publish
        
        gets the saved socket for the server,
        sends request to publish the article,
        and returns the response
        
        return:
        0: FAILED TO PUBLISH
        1: SUCCESS TO PUBLISH
        '''
        
        # checks whether the client has joined the server 
        if self.activeServers[s_no].addr not in self.servers:
            return 0
        
        # saved client server socket
        clientServerSocket = self.servers[self.activeServers[s_no].addr]
        
        # send the publish request
        message_content = {
            "reqType": REQUEST.PublishArticle.value,
            "clientUUID": self.client_id,
            "article": article
        }
        pickled_message = pickle.dumps(message_content)
        clientServerSocket.send(pickled_message)
        
        #  waits for the server response
        pickledRecvMsg = clientServerSocket.recv()
        recvMsg = pickle.loads(pickledRecvMsg)
            
        return recvMsg["status"]
        
      
if __name__ == "__main__":
    # creates an instance for the server
    client = Client()
    
    # menu
    while True:
        print("Welcome!!! Here are your choices:")
        print("[1] List of servers")
        print("[2] Join Server")
        print("[3] Leave Server")
        print("[4] Get Articles")
        print("[5] Publish Article")
        print("[6] Exit")
        req = int(input("Enter your choice: ")) + 1
        
        if req == REQUEST.GetServerList.value:
            client.getServerList()
            if len(client.activeServers) == 0:
                print("\nNo active servers\n")
            else:
                print("\nHere are the active servers:")
                for i, node in enumerate(client.activeServers):
                    print(str(i+1) + ".", end =" ")
                    print(node)
                print()
                
        elif req == REQUEST.JoinServer.value:
            s_no = int(input("Enter server number: ")) - 1
            
            if s_no < 0 or s_no >= len(client.activeServers):
                # incorrect server index
                print("\nNo such server exist\n")
                
            elif client.joinServer(s_no):
                # successful to join the server
                print("\nJoining the server: SUCCESS\n")
            else:
                # failed to join the server
                print("\nJoining the server: FAILED\n")
            
        elif req == REQUEST.LeaveServer.value:
            s_no = int(input("Enter server number: ")) - 1
            
            if s_no < 0 or s_no >= len(client.activeServers):
                # incorrect server index
                print("\nNo such server exist\n")
                
            elif client.leaveServer(s_no):
                # successful to leave the server
                print("\nLeaving the server: SUCCESS\n")
            else:
                # failed to leave the server
                print("\nLeaving the server: FAILED\n")
                
        elif req == REQUEST.GetArticles.value:
            s_no = int(input("Enter server number: ")) - 1
            
            if s_no < 0 or s_no >= len(client.activeServers):
                # incorrect server index
                print("\nNo such server exist\n")
                
            else:
                print("Specify the article request")
                type = input("")
                author = input("")
                time = input("")
                
                articleRequest = ArticleRequest(type, author, time)
                articles = client.getArticles(s_no, articleRequest)
           
                if articles != 0:
                    # successful to get the articles
                    
                    if len(articles) == 0:
                        print("\nNo articles found\n")
                    else: 
                        print("\nHere are the articles:")
                        for i, article in enumerate(articles):
                            print(str(i+1) + ")", end ="")
                            print(article)
                        print()
                    
                else:
                    # failed to get the articles
                    print("\nGetting the articles: FAILED\n")
            
        elif req == REQUEST.PublishArticle.value:
            s_no = int(input("Enter server number: ")) - 1
            
            if s_no < 0 or s_no >= len(client.activeServers):
                # incorrect server index
                print("\nNo such server exist\n")
                
            else:
                print("Write down the article")
                type = input("")
                author = input("")
                time = input("")
                content = input("")
                
                try:
                    article = Article(type, author, time, content)
                    if client.publishArticle(s_no, article):
                        # successful to leave the server
                        print("\nPublishing the article: SUCCESS\n")
                    else:
                        # failed to leave the server
                        print("\nPublishing the article: FAILED\n")
                    
                except ValueError:
                    print("\nIllegal Format\n")
            
        elif req == REQUEST.PublishArticle.value:
            break
        else:
            print("\nInvalid Option\n")
