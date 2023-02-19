import pika
import json
from article import Article
import os
from dotenv import load_dotenv
from datetime import date,datetime

# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Connect the path with your '.env' file name
load_dotenv(os.path.join(BASEDIR, '.env'))

REGISTER_SERVER=os.environ.get('REGISTER_SERVER')
SEND_ARTICLES=os.environ.get('SEND_ARTICLES')
RECEIVE_ARTICLE=os.environ.get('RECEIVE_ARTICLE')
REGISTER_CLIENT=os.environ.get('REGISTER_CLIENT')
LEAVE_SERVER=os.environ.get('LEAVE_SERVER')
PUBLISH_ARTICLE=os.environ.get('PUBLISH_ARTICLE')
SEND_ARTICLES=os.environ.get('SEND_ARTICLES')
SPORT=os.environ.get('SPORT')
FASHION=os.environ.get('FASHION')
POLITICS=os.environ.get('POLITICS')
NONE=os.environ.get('NONE')

MAXCLIENTS=5 # maximum number of clients

CONNECTED_CLIENTS=set()

CLIENTS_ARTICLES=dict()

class server():
    def __init__(self,queue_name):
        self.queue_name=queue_name
        conn_params=pika.ConnectionParameters('localhost')
        self.connection=pika.BlockingConnection(conn_params)
        self.channel=self.connection.channel()
        self.hostname=conn_params.host
        
        self.channel.queue_declare(queue=self.queue_name,exclusive=True)
        
        def receive_message(ch,method,properties,body):

            data=json.loads(body)

            

            if data['type']==REGISTER_SERVER:
                success=data['success']

                if success==True:
                    print("SUCCESS")
                else:
                    print("FAIL")
                    print(data['message'])
                    self.channel.stop_consuming()
                    self.connection.close()

            elif data['type']==REGISTER_CLIENT:
                client_uuid=data['uuid']
                routing_key=data['routing_key']

                server=(self.hostname,self.queue_name)

                message={'type':REGISTER_CLIENT,'server':server}

                print(f"JOIN REQUEST FROM {client_uuid}")

                if len(CONNECTED_CLIENTS)<MAXCLIENTS:
                    CONNECTED_CLIENTS.add(client_uuid)
                    message['success']=True

                else:
                    message['success']=False
                    message['message']='Server max limit reached ...'
                    
                self.channel.basic_publish(exchange='',routing_key=routing_key,
                    body=json.dumps(message))

            elif data['type']==LEAVE_SERVER:
                client_uuid=data['uuid']
                routing_key=data['routing_key']
                server=(self.hostname,self.queue_name)

                message={'type':LEAVE_SERVER,'server':server}

                print(f"LEAVE REQUEST FROM {client_uuid}")

                if client_uuid in CONNECTED_CLIENTS:
                    CONNECTED_CLIENTS.remove(client_uuid)
                    message['success']=True
                else:
                    message['success']=False
                    message['message']='Client not connected...'
                
                self.channel.basic_publish(exchange='',routing_key=routing_key, 
                    body=json.dumps(message)
                )

            # fanout article to all queues
            elif data['type']==RECEIVE_ARTICLE:

                message={'type':RECEIVE_ARTICLE}
                client_uuid=data['uuid']
                routing_key=data['routing_key']
                
                print(f"ARTICLES REQUEST FROM {client_uuid}")

                if client_uuid not in CONNECTED_CLIENTS:
                    message['success']=False
                    message['message']='Client is not connected to the Server ...'
                
                else:
                    received_article=json.loads(data['article'])
                    article_type='< >'if received_article['article_type']==NONE  else  received_article['article_type']
                    author='< >' if received_article['author']==NONE else received_article['author']

                    print(f"FOR {article_type}, {author}, {received_article['time']}")

                    message['all_articles']=self.send_articles(received_article['article_type'],received_article['author'],received_article['time'])

                    message['success']=True

                self.channel.basic_publish(exchange='',routing_key=routing_key,body=json.dumps(message,default=vars))
                

            # receive article and store in database
            elif data['type']==PUBLISH_ARTICLE:
                message={'type':PUBLISH_ARTICLE}
                client_uuid=data['uuid']
                routing_key=data['routing_key']

                print(f"ARTICLES PUBLISH FROM {client_uuid}")

                if client_uuid not in CONNECTED_CLIENTS:
                    message['success']=False
                    message['message']='Client is not connected to the Server ...'

                else:
                    
                    received_article=json.loads(data['article'])

                    if client_uuid not in CLIENTS_ARTICLES:
                        CLIENTS_ARTICLES[client_uuid]=[]

                    date_g=date.today()

                    new_article=Article(received_article['article_type'],received_article['author'],date_g,received_article['content'])

                    CLIENTS_ARTICLES[client_uuid].append(new_article)
                    
                    message['success']=True
                
                self.channel.basic_publish(exchange='',routing_key=routing_key,body=json.dumps(message))

        self.channel.basic_consume(queue=self.queue_name,on_message_callback=receive_message,auto_ack=True)
        
        self.register_server(self.queue_name)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Closing the connection ... ")
            self.channel.stop_consuming()
            self.connection.close()

    # function to register the server
    def register_server(self,queue_name):
        queue1='registry_server'
        message={'type':REGISTER_SERVER,'server_name':self.hostname,'routing_key':queue_name}
        self.channel.basic_publish(exchange='',routing_key=queue1,body=json.dumps(message))


    # function to send articles to all clients
    def send_articles(self,article_type,author,date):

        final_data=[]
        date=datetime.strptime(date, "%Y-%m-%d").date()

        for client in CLIENTS_ARTICLES.keys():
            for client_article in CLIENTS_ARTICLES[client]:
                client_date=datetime.strptime(str(client_article.time), "%Y-%m-%d").date()

                if client_date>date and (author==NONE or client_article.author==author) and (article_type==NONE or client_article.article_type==article_type):

                    final_data.append(client_article)
        
        for article in final_data:
            article.time=str(article.time)

        return tuple(final_data)


if __name__=='__main__':
    queue_name=input("Enter queue name: ")
    server(queue_name)

# functionality
# connect to registry server
# receive articles from clients
# send articles to clients