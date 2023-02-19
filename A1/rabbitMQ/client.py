import pika
import json
from article import Article
import os
from dotenv import load_dotenv
import uuid 
from datetime import date,datetime

# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Connect the path with your '.env' file name
load_dotenv(os.path.join(BASEDIR, '.env'))


SERVER_LIST=os.environ.get('SERVER_LIST')
REGISTER_CLIENT=os.environ.get('REGISTER_CLIENT')
LEAVE_SERVER=os.environ.get('LEAVE_SERVER')
SPORT=os.environ.get('SPORT')
FASHION=os.environ.get('FASHION')
POLITICS=os.environ.get('POLITICS')
NONE=os.environ.get('NONE')
PUBLISH_ARTICLE=os.environ.get('PUBLISH_ARTICLE')
SEND_ARTICLES=os.environ.get('SEND_ARTICLES')
RECEIVE_ARTICLE=os.environ.get('RECEIVE_ARTICLE')

class Client():
    def __init__(self,queue_name):
        self.queue_name=queue_name
        conn_params=pika.ConnectionParameters('localhost')
        self.SERVERS=dict()
        self.JOINED_SERVERS=dict() # use for publishing or getting the articles
        self.connection=pika.BlockingConnection(conn_params)
        self.channel=self.connection.channel()
        self.host_name=conn_params.host
        self.client_uuid=str(uuid.uuid4())
        self.channel.queue_declare(queue=self.queue_name,exclusive=True)

    def get_servers_address(self,server_set):

        while True:
            serverIndex = int(input("Please enter to which you want to connect or leave : "))
            
            if serverIndex in server_set:
                return server_set[serverIndex]
            else:
                print('Please enter the correct value : ')
    

    def callback_fun(self,ch,method,props,body):
   
        data=json.loads(body)

        if data['type']==SERVER_LIST:
            data=data['server_list']
            self.handle_server_list(data)

        elif data['type']==REGISTER_CLIENT or data['type']==LEAVE_SERVER:
            success=data['success']
            if success:
                print("SUCCESS")

                if data['type']==LEAVE_SERVER:
                    server=(data['server'][0],data['server'][1])
                    
                    for i in self.JOINED_SERVERS.keys():
                        if self.JOINED_SERVERS[i]==server:
                            del self.JOINED_SERVERS[i]
                            break

                elif data['type']==REGISTER_CLIENT:
                    server=(data['server'][0],data['server'][1])
                    
                    present=False
                    for i in self.JOINED_SERVERS.keys():

                        if self.JOINED_SERVERS[i]==server:
                            present=True
                            break
                    
                    if not present:
                        self.JOINED_SERVERS[len(self.JOINED_SERVERS)+1]=server
                    
            else:
                print("FAIL")
                print(data['message'])

        elif data['type']==PUBLISH_ARTICLE:
            if data['success']:
                print("SUCCESS")
            
            else:
                print("FAIL")
                print(data['message'])

        elif data['type']==RECEIVE_ARTICLE:
            all_articles=data['all_articles']
            
            i=1
            for article in all_articles:
                print(i,") ",article['article_type'])
                print(article['author'])
                print(article['time'])
                print(article['content'])
                i+=1


    def handle_server_list(self,data):
        print("Here is the list of active servers:")

        for i in range(0,len(data)):
            self.SERVERS[i+1]=(data[i][0],data[i][1])
        
        for i in self.SERVERS.keys():
            server_name=self.SERVERS[i][0]
            routing_key=self.SERVERS[i][1]

            print(f"{i}.ServerName{i}-{server_name} having routing_key: {routing_key}")

    def send_message(self,message,server_routing_key):
        self.channel.basic_publish(exchange='',routing_key=server_routing_key,body=json.dumps(message))

        self.channel.basic_consume(queue=self.queue_name,on_message_callback=self.callback_fun,auto_ack=True)

        # replace for start_consuming blocking call
        self.channel.connection.process_data_events(time_limit=1)


    def server_list(self):
        queue1='registry_server'
    
        message={'type':SERVER_LIST,'host':self.host_name,'routing_key':self.queue_name}

        self.send_message(message,queue1)

    def join_server(self,server):
        
        server_routing_key=server[1]
        message={'type':REGISTER_CLIENT,'uuid':self.client_uuid,'routing_key':self.queue_name}

        self.send_message(message,server_routing_key)

    def leave_server(self,server):
        # remove server from JOINED_SERVERS
        # send request to server
        server_routing_key=server[1]

        message={'type':LEAVE_SERVER,'uuid':self.client_uuid,'routing_key':self.queue_name}

        self.send_message(message,server_routing_key)

    def validate_date(self,date_text):
        try:
            if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
                raise ValueError
            return True
        except ValueError:
            return False

    def get_articles(self,server):
        idx = int(input("""
            Enter the type of Article
            [1] Sport
            [2] Fashion
            [3] Politics
            [4] None\n"""))

        if idx == 1:
            type =SPORT
        elif idx == 2:
            type = FASHION
        elif idx == 3:
            type = POLITICS
        else:
            type = NONE

        author = input("Enter the Author's Name: ")

        # if user skips to enter author name, then set user=none
        if len(author)==0:
            author=NONE

        date = input("Enter the date in YYYY-MM-DD format: ")

        while not self.validate_date(date):
            date=input("Enter the date in YYYY-MM-DD format: ")

        server_routing_key=server[1]

        article=Article(type,author,date,'')

        message={'type':RECEIVE_ARTICLE,'uuid':self.client_uuid,'routing_key':self.queue_name,'article':json.dumps(article,default=vars)}

        self.send_message(message,server_routing_key)

    def publish_article(self,server):
        idx = int(input("""
        Enter the type of Article
        [1] Sport 
        [2] Fashion
        [3] Politics\n"""))

        
        if idx == 1:
            type = SPORT

        elif idx == 2:
            type = FASHION

        elif idx==3:
            type = POLITICS
        
        
        author = input("Enter the Author's Name : ")
        context = input("Enter the content in NOT more than 200 words : ")

        server_routing_key=server[1]
        
        article=Article(type,author,'',context)

        message={'type':PUBLISH_ARTICLE,'uuid':self.client_uuid,'routing_key':self.queue_name,'article':json.dumps(article,default=vars)}

        self.send_message(message,server_routing_key)

client=None

def main():
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

        if OPERATION==1:
            client.server_list()
        
        # join server
        elif OPERATION==2:
            
            if len(client.SERVERS)==0:
                print("No server is available ...")
                continue
                
            for i in client.SERVERS.keys():
                print(f"{i}. {client.SERVERS[i][0]} having priority_queue {client.SERVERS[i][1]}")
                i+=1

            server=client.get_servers_address(client.SERVERS)

            client.join_server(server)

        # leave server
        elif OPERATION==3:
            
            if len(client.JOINED_SERVERS)==0:
                print("No server is available ...")
                continue
                
            
            for i in client.JOINED_SERVERS.keys():
                print(f"{i}. {client.JOINED_SERVERS[i][0]} having priority_queue {client.JOINED_SERVERS[i][1]}")
                
            leave_server=client.get_servers_address(client.JOINED_SERVERS)

            
            client.leave_server(leave_server)


        # get the articles
        elif OPERATION==4:
            if len(client.JOINED_SERVERS)==0:
                print("No server is available ...")
                continue
                
            
            for i in client.JOINED_SERVERS.keys():
                print(f"{i}. {client.JOINED_SERVERS[i][0]} having priority_queue {client.JOINED_SERVERS[i][1]}")
            
            server=client.get_servers_address(client.JOINED_SERVERS)
            client.get_articles(server)

        # publish the articles
        elif OPERATION==5:
            if len(client.JOINED_SERVERS)==0:
                print("No server is available ...")
                continue
                
            
            for i in client.JOINED_SERVERS.keys():
                print(f"{i}. {client.JOINED_SERVERS[i][0]} having priority_queue {client.JOINED_SERVERS[i][1]}")
            
            server=client.get_servers_address(client.JOINED_SERVERS)

            client.publish_article(server)

        elif OPERATION==6:
            print("Goodbye ...")
            client.connection.close()
            return

if __name__=='__main__':
    queue_name=input("Enter queue name: ")
    client=Client(queue_name)
    main()