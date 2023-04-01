import client
import os
import sys

def simulate():
    # running a registry server
    os.system("start cmd /K python registry_server.py")
    print(f"Registry Server is running")
    
    input('Press any key to continue...')
    
    # running N replicas
    N = 3
    for idx in range(N):
        os.system("start cmd /K python replica.py")
        print(f"Replica-{idx+1} is running")
    
    input('Press any key to continue...')
    
    # input test file
    sys.stdin = open("test_input.txt", "r")

    # let the client run some tests cases 
    status = client.run_test_cases(sleep_timer=5)    
    if status:
        print("Tests cases PASSED!")
    else:
        print("Tests cases FAILED!")
    
    
if __name__ == '__main__':
    simulate()