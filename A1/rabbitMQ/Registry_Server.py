import pika
import json
import os
from dotenv import load_dotenv

# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Connect the path with your '.env' file name
load_dotenv(os.path.join(BASEDIR, '.env'))


MAXSERVERS=5
SERVER_LIST=os.environ.get('SERVER_LIST')
REGISTER_SERVER=os.environ.get('REGISTER_SERVER')


SERVERS=set()

class Registry_Server():
    def __init__(self,queue_name):
        self.queue_name=queue_name
        self.connection=pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel=self.connection.channel()

        self.channel.queue_declare(queue=self.queue_name,exclusive=True)
        

        def receive_message(ch,method,properties,body):
            data=json.loads(body)

            if data['type']==SERVER_LIST:
                queue_send=data['routing_key']
                host_name=data['host']
                
                self.server_list(queue_send,host_name)

            elif data['type']==REGISTER_SERVER:
                server_name=data['server_name']
                routing_key=data['routing_key']
        
                self.register_server(server_name,routing_key)
            
            
        
        self.channel.basic_consume(queue=self.queue_name,on_message_callback=receive_message,auto_ack=True)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
        except Exception as e:
            print(e)
            print("Closing the connection ....")
            self.channel.stop_consuming()
            self.connection.close()

    def server_list(self,routing_key,host_name):
        print(f"SERVER LIST REQUEST FROM {host_name} having routing_key: {routing_key}")

        
        server_list=list()

        for server in SERVERS:
            server_list.append(server)

        message={'type':SERVER_LIST,'server_list':server_list}
        
        self.channel.basic_publish(exchange='',routing_key=routing_key,body=json.dumps(message))

    def register_server(self,server_name,routing_key):
    
        register_response={'type':REGISTER_SERVER}
        print(f"JOIN REQUEST FROM {server_name} having routing_key: {routing_key}")

        if len(SERVERS)<MAXSERVERS:
            
            server=(server_name,routing_key)
            SERVERS.add(server)

            register_response['success']=True

        else:
            register_response['success']=False
            register_response['message']='Max Server limit reached. Try Again after some time ...'

        self.channel.basic_publish(exchange='',routing_key=routing_key,body=json.dumps(register_response))

            
if __name__=='__main__':
    Registry_Server('registry_server')

# functionality
# register server
# send server list to clients


