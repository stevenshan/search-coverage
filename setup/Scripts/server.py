# modules for socket
import socket, select, sys

# module for interacting with Unreal
import unreal

def connect_mesg (sock):
    print("Client (%s, %s) connected" % sock)

def disconnect_mesg (sock):
    print("Client (%s, %s) is offline" % sock)

def log_mesg (mesg):
    print(mesg.rstrip("\n\r"))

def disconnect (socket):
    socket.close()
    if socket in CONNECTION_LIST:
        CONNECTION_LIST.remove(socket)
    disconnect_mesg(addr)

# function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
    # don't send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except:
                # broken socket connection may be, chat client pressed ctrl+c for example
                disconnect(socket)

# function to send data to specific socket
def broadcast_data_to (sock, message):
    if sock != server_socket:
        try:
            if message[-1] != "\n":
                message += "\n"
            sock.send(str.encode(message))
        except:
            disconnect(sock)

# handler for receiving mesg from sock
def receive_data (sock, mesg):
    # log message
    log_mesg("\r" + '<' + str(sock.getpeername()) + '> ' + data)

    response = unreal.send_command(mesg)
    if response != None:
        broadcast_data_to(sock, response)
 
if __name__ == "__main__":
     
    if (len(sys.argv) == 2):
        PORT = int(sys.argv[1])
    else:
        PORT = 5000

    # list to keep track of socket descriptors
    CONNECTION_LIST = []
    RECV_BUFFER = 4096 
     
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    log_mesg("Listening on port " + str(PORT))
 
    while 1:
        # get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[], 0)

        for sock in read_sockets:
            # new connection
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                connect_mesg(addr)
             
            # some incoming message from a client
            else:
                # data recieved from client, process it
                try:
                    data = sock.recv(RECV_BUFFER).decode("utf-8")
                    if data:
                        receive_data(sock, data)
                 
                except Exception as e:
                    disconnect(sock)
                    continue
     
    server_socket.close()