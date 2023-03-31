import threading
import subprocess
import multiprocessing
import RegistryServer
import Server
import Client
import sys
sys.path.insert(1, "../")
import A2_pb2
import A2_pb2_grpc
import time


def simulate():
    IP = "localhost"
    registryServerPort = "6000"

    subprocesses = []
    
    # create registry server
    subprocess.Popen(['gnome-terminal', '--', 'python', 'RegistryServer.py', IP, registryServerPort])

    # create replica servers
    N = int(input("Enter the number of replicas: "))
    for i in range(N):
        subprocess.Popen(['gnome-terminal', '--', 'python', 'Server.py'])
        
    time.sleep(5)

    # create client
    Client.automation()

if __name__ == '__main__':
    simulate()