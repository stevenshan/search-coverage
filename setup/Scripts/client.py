# telnet program example
import socket, select, string, sys
import os
from threading import *

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import pickle, struct

def send_msg(sock):
    while True:
        data = sys.stdin.readline().replace("\n", "")
        if data == "exit":
            os._exit(1)
        print(">", data, data == "test")
        if data == "test":
            # set texture/plot dimensions and dpi, ensure dpi is a float !
            width = 256 
            height = 256
            dpi = 50.0

            # create a new figure with the specified sizes
            fig = plt.figure(1)
            fig.set_dpi(dpi)
            fig.set_figwidth(width/dpi)
            fig.set_figheight(height/dpi)

            # plot a simple graph with a label on the y axis
            plt.plot([1, 2, 3, 4])
            plt.ylabel('some numbers')
            fig.canvas.draw()

            data = (((0, None),(1, "figure")), ("displayGraph", fig.canvas.buffer_rgba()))
        else:
            data = (((0, None),), (data,))

        data = pickle.dumps(data)
        msg = struct.pack('>I', len(data)) + data
        sock.sendall(msg)

def recv_msg(sock):
    while True:
        data = sock.recv(4096)
        sys.stdout.write("<Server> " + data.decode("utf-8"))
 
#main function
if __name__ == "__main__":
     
    if (len(sys.argv) == 1):
        host = "localhost"
        port = 4001
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
       