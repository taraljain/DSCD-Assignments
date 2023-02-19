from helper import REQUEST, Node
import pickle
import zmq
    
class RegistryServer:
    def __init__(self, maxServers):
        '''
        initializes the registry server,
        binds it to a port
        '''
        self.maxServers = maxServers
        self.totalServers = 0
        self.activeServers = []
        
        self.context = zmq.Context.instance()
        self.registryServer = self.context.socket(zmq.REP)
        self.registryServer.bind("tcp://127.0.0.1:8000")
        print("Registry Server running on tcp://127.0.0.1:8000")
    
    def isServerRegistered(self, serverNode):
        '''
        paramter:
        serverNode: server node
        
        checks if the server is registered or not
        
        return:
        0/1 boolean value
        
        '''
        for node in self.activeServers:
            if node.addr == serverNode.addr:
                return 1
        return 0
    
    def serve(self):
        '''
        waits for the requests from servers/clients 
        '''

        while True:
            #  waits for the next request from servers/clients
            pickledRecvMsg = self.registryServer.recv()
            recvMsg = pickle.loads(pickledRecvMsg)
            
            # parse request type, and calls respective functions
            reqType = recvMsg["reqType"]
            if reqType == REQUEST.Register.value:
                self.registerServer(recvMsg)
            elif reqType == REQUEST.GetServerList.value:
                self.getServerList(recvMsg)
                
    def registerServer(self, recvMsg):
        '''
        paramters:
        registryServer: socket bind to the registry server
        recvMsg: received message from a server
        
        parse out the recv msg to get server name and addr,
        sends back SUCCESS if total no of servers <= max no of servers
        
        return:
        STATUS: 0 or 1
        '''
        
        # parsing out server info
        status = 0
        serverName = recvMsg["serverName"]
        serverAddr = recvMsg["serverAddr"]
        print("JOIN REQUEST FROM " + serverAddr)
        
        # checking if total count < max count of servers
        if self.totalServers < self.maxServers:
            # checks if server is already registered or not
            if not self.isServerRegistered(Node(serverName, serverAddr)):
                self.activeServers.append(Node(serverName, serverAddr))              
                self.totalServers += 1
            status = 1

        # sending the response back to server
        sendMsg = {
            "status": status
        }
        pickledSendMsg = pickle.dumps(sendMsg)
        self.registryServer.send(pickledSendMsg)
        
    def getServerList(self, recvMsg):
        '''
        paramters:
        recvMsg: received message from a client
        
        parse out the recv msg to get client name and addr,
        sends back the list of active registered servers to the client
        '''
        clientAddr = recvMsg["clientAddr"]
        print("SERVER LIST REQUEST FROM " + str(clientAddr))
    
        sendMsg = {
            "activeServers": self.activeServers
        }
        pickledSendMsg = pickle.dumps(sendMsg)
        self.registryServer.send(pickledSendMsg) 
    
if __name__ == "__main__":
    # creates an instance for the registry server
    registryServer = RegistryServer(maxServers=2)
    # starts the registry server
    registryServer.serve()        
