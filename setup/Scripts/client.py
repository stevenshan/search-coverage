# telnet program example
import socket, select, string, sys

from threading import *

import pickle

def send_msg(sock):
    while True:
        data = sys.stdin.readline()
        data = (((0, None),(1, None)), (data.replace("\n", ""), [1, 2, 3]))
        sock.send(pickle.dumps(data))
        
def recv_msg(sock):
    while True:
        data = sock.recv(4096)
        sys.stdout.write("<Server> " + data.decode("utf-8"))
 
#main function
if __name__ == "__main__":
     
    if (len(sys.argv) == 1):
        host = "localhost"
        port = 4000
        print('Usage : python client.py hostname ' + host)
        print("Using default values localhost and port " + str(port))
    elif(len(sys.argv) < 3) :
        print('Usage : python client.py hostname port')
        sys.exit()
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print('Unable to connect')
        sys.exit()
     
    print('Connected to remote host. Start sending messages')

    Thread(target=send_msg, args=(s,)).start()  
    Thread(target=recv_msg, args=(s,)).start()
       