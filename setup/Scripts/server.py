# modules for socket
import socket, select, sys

# module for interacting with Unreal
import unreal

def connect_mesg (sock):
    unreal.connect_mesg("Client (%s, %s) connected" % sock)

def disconnect_mesg (sock):
    unreal.disconnect_mesg("Client (%s, %s) is offline" % sock)

def log_mesg (mesg):
    unreal.log_mesg(mesg.rstrip("\n\r"))

class Server:
    RECV_BUFFER = 4096
    def __init__ (self, port = 5000):

        # list to keep track of socket descriptors
        CONNECTION_LIST = []
         
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(10)
     
        # add server socket to the list of readable connections
        CONNECTION_LIST.append(server_socket)
     
        log_mesg("Listening on port " + str(port))
     
        self.sock = server_socket
        self.conn_list = CONNECTION_LIST
        self.conn_addr = {}

    def stop (self):
        self.sock.close()

    def listen (self):
        # get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(self.conn_list,[],[], 0)

        for sock in read_sockets:
            # new connection
            if sock == self.sock:
                sockfd, addr = self.sock.accept()
                self.conn_addr[sockfd] = addr
                self.conn_list.append(sockfd)
                connect_mesg(addr)
             
            # some incoming message from a client
            else:
                # data recieved from client, process it
                try:
                    data = sock.recv(self.RECV_BUFFER).decode("utf-8")
                    if data:
                        self.receive_data(sock, data)
                 
                except:
                    self.disconnect(sock)
                    continue

    def disconnect (self, socket):
        socket.close()
        if socket in self.conn_list:
            self.conn_list.remove(socket)
        disconnect_mesg(self.conn_addr[socket])
        self.conn_addr.pop(socket, None)

    # function to broadcast chat messages to all connected clients
    def broadcast_data (self, sock, message):
        # don't send the message to master socket and the client who has send us the message
        for socket in CONNECTION_LIST:
            if socket != self.sock and socket != sock :
                try :
                    socket.send(message)
                except:
                    # broken socket connection may be, chat client pressed ctrl+c for example
                    self.disconnect(socket)

    # function to send data to specific socket
    def broadcast_data_to (self, sock, message):
        if sock != self.sock:
            try:
                if message[-1] != "\n":
                    message += "\n"
                sock.send(str.encode(message))
            except:
                self.disconnect(sock)

    # handler for receiving mesg from sock
    def receive_data (self, sock, mesg):
        # log message
        log_mesg("\r" + '<' + str(sock.getpeername()) + '> ' + mesg)

        response = unreal.send_command(mesg)
        if response != None:
            self.broadcast_data_to(sock, str(response))

if __name__ == "__main__":
    server = Server()
    while (1):
        server.listen()
    server.stop()
