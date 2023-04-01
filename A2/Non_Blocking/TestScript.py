import subprocess
import client
import time


def simulate():
    IP = "localhost"
    registryServerPort = "6000"
    
    # create registry server
    subprocess.Popen(['gnome-terminal', '--', 'python', 'registry_server.py', IP, registryServerPort])

    # create replica servers
    N = int(input("Enter the number of replicas: "))
    for i in range(N):
        subprocess.Popen(['gnome-terminal', '--', 'python', 'server.py'])
        
    time.sleep(5)

    # create client
    client.automation()

if __name__ == '__main__':
    simulate()