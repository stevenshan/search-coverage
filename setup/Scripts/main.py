import unreal_engine as ue

# modules for socket
import socket, select, sys

# to receive structured messages
import pickle, struct

import re
from Pixel_Image import Pixel, Image, DEFAULT_DIMENSION

from unreal_engine.classes import MaterialInstance
from unreal_engine import FColor, FLinearColor
from unreal_engine.enums import EBlendMode, EPixelFormat

# used to display graph
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# predeclare commands variable
commands = {}

# global parameters
global_parameters = {
    "logging": True,
    "root": None
}

'''
Begin Available Commands
'''

def _help (params):
    return str([x for x in commands])

def _print (params):
    ue.print_string(params["mesg"])

def _toggle_log (params):
    if params["value"] == "on":
        global_parameters["logging"] = True
    elif params["value"] == "off":
        global_parameters["logging"] = False 
    return "Logging is " + ("on" if global_parameters["logging"] else "off")

def _get_ortho_width (params):
    root = global_parameters["root"]
    if root == None:
        return "Error: no root uobject"
    try:
        orthowidth = root.uobject.get_owner().mapCapture.get_property('OrthoWidth')
    except:
        return "Error: could not get orthographic width"

    result = ""
    try:
        result = str(int(orthowidth))
    except:
        return "Error: could not convert orthographic width to string"
    else:
        return result

def _set_ortho_width(params):
    root = global_parameters["root"]
    if root == None:
        return "Error: no root uobject"
    try:
        root.uobject.get_owner().mapCapture.set_property('OrthoWidth', float(params["width"]))
    except Exception as e:
        return "Error: " + str(e)
    else:
        return "Success"

def _display_graph(params):
    root = global_parameters["root"]
    try:
        if not root.mat_valid:
            return "Error: could not load material"
        root.texture.texture_set_data(params["figure"])
    except Exception as e:
        return "Error: Could not draw graph; " + str(e)
    else:
        return "Success"

def _display_pdf(params):
    root = global_parameters["root"]
    try:
        if not root.mat_valid:
            return "Error: could not load material"
        root.pdftexture.texture_set_data(params["figure"])
    except Exception as e:
        return "Error: Could not draw graph; " + str(e)
    else:
        return "Success"
    
'''
End Available Commands
'''

# dictionary of available commands
commands = {
    "help": [_help, [], {}],
    "print": [_print, ["mesg"], {}],
    "log": [_toggle_log, ["value"], {"value": ""}],
    "getOrthoWidth": [_get_ortho_width, [], {}],
    "setOrthoWidth": [_set_ortho_width, ["width"], {"width": 6000}],
    "displayGraph": [_display_graph, ["figure"], {}],
    "displayPDF": [_display_pdf, ["figure"], {}]
}

class unreal:
    @staticmethod
    def connect_mesg (mesg):
        ue.print_string(mesg)

    @staticmethod
    def disconnect_mesg (mesg):
        ue.print_string(mesg)

    @staticmethod
    def log_mesg (mesg):
        if global_parameters["logging"]:
            ue.print_string(mesg)

# try to match labels with params
def format_params(labels, defaults, params):
    final_params = {}
    for i in range(1, len(params)):
        if params[i][1] != "":
            if params[i][0] in labels:
                final_params[params[i][0]] = params[i][1]
            else:
                raise ValueError("Error: unknown key '" + params[i][0] + "'")

    i = 1 
    for j in range(len(labels)):
        key = labels[j]
        if key not in final_params:
            param = None
            while i < len(params) and params[i][1] != "":
                i += 1
            if i < len(params):
                param = params[i][0]
                i += 1
            elif key in defaults:
                param = defaults[key]
            else:
                raise ValueError("Error: not enough parameters supplied")
            final_params[key] = param

    return final_params

def send_command (mesg):
    # receive message as pickled structure documented above Server.receive_data

    command = None
    formatted_params = None

    # try to decode data into format shown above
    try:
        # plain message command
        if (len(mesg[0]) == 1):
            mesg = mesg[1][0]
            # split mesg into comamand and parameters
            try:
                params = re.findall("(\"([^\"]*)\"|([^ =]+)[=]?\"([^\"]*)\"|([^ =]+)[=]?([^ ]*))", 
                                    mesg.replace("\n", ""))
                for i in range(len(params)):
                    param = params[i]
                    if param[-1] == "" and param[-2] == "":
                        if param[-3] == "":
                            params[i] = (param[1], "")
                        else:
                            params[i] = (param[2], param[3])
                    elif param[-1] == "":
                        params[i] = (param[-2], "")
                    else:
                        params[i] = (param[-2], param[-1])
            except Exception as e:
                return "Error: couldn't properly regex command message"

            # make sure params is not zero length and first parameter is singleton
            if len(params) == 0 or params[0][1] != "":
                return "Error: improperly formatted command"
            elif params[0][0] not in commands:
                return "Error: command '" + params[0][0] + "' does not exist"

            # format parameters
            command = commands[params[0][0]]
            formatted_params = format_params(command[1], command[2], params)
        else:
            if mesg[1][0] not in commands:
                return "Error: command '" + str(mesg[1][0]) + "' does not exist"

            command = commands[mesg[1][0]]
            formatted_params = {}

            # try to format parameters
            entries_index = 1
            for i in range(1, len(mesg[0])):
                if mesg[0][i][1] != None:
                    if mesg[0][i][1] not in command[1]:
                        return "Error: unknown parameter"
                    else:
                        formatted_params[mesg[0][i][1]] = mesg[1][i]
            for key in command[1]:
                if key not in formatted_params:
                    if key in command[2]:
                        formatted_params[key] = command[2][key]
                    elif entries_index >= len(mesg[0]):
                        return "Error: not enough parameters supplied"
                    else:
                        formatted_params[key] = mesg[1][entries_index]
                        entries_index += 1
    except Exception as e:
        return "Error: unknown error occurred: " + str(e)

    # try to run the command with the parameters
    try:
        return command[0](formatted_params)
    except ValueError as e:
        return str(e)
    except Exception as e:
        ue.print_string(e)
        return "Error: command could not be executed"


def connect_mesg (sock):
    unreal.connect_mesg("Client (%s, %s) connected" % sock)

def disconnect_mesg (sock):
    unreal.disconnect_mesg("Client (%s, %s) is offline" % sock)

def log_mesg (mesg):
    unreal.log_mesg(mesg.rstrip("\n\r"))

'''
Method for receiving data from socket
https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
'''
def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

# used for sending and receiving messages
class Server:
    RECV_BUFFER = 4096
    def __init__ (self, port = 4001):
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
                    data = recv_msg(sock)
                    if data:
                        self.receive_data(sock, data)
                 
                except Exception as e:
                    ue.print_string(str(e))
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

    '''
    Structure of data:
    Tuple(
        ((Type1, Var1), (Type2, Var2), (Type3, Var3), ...),
        (Data1, Data2, Data3, ...)
    )
    where Type:
        0 => string
        1 => list
    and Var1 is a string corresponding to which parameter to bind to
    and Data is corresponding value
    note: raw command as string can be sent as ((0, None), ("blah blah"))
    command name must be Data1
    '''
    # handler for receiving mesg from sock
    def receive_data (self, sock, mesg):
        # decode data
        try:
            raw_data = pickle.loads(mesg)
        except Exception as e:
            self.broadcast_data_to(sock, "Error: could not unpack data")
            return

        try:
            if len(raw_data[0]) == 0:
                raise ValueError("Error: no parameters")
            elif len(raw_data[0]) != len(raw_data[1]):
                ue.print_string(str(raw_data))
                raise ValueError("Error: input not well formatted")
            elif raw_data[0][0][0] != 0:
                raise ValueError("Error: no command found")
        except ValueError as e:
            response = e
        else:
            response = send_command(raw_data)

        self.broadcast_data_to(sock, ">" + (str(response) if response != None else ""))

        log_mesg("\r" + '<' + str(sock.getpeername()) + '> sent a message')

# main module that is imported into Unreal Editor
class STOEC:
    def begin_play(self):
        self.server = Server()
        global_parameters["root"] = self


        # initialize texture for graph
        self.texture = ue.create_transient_texture(DEFAULT_DIMENSION, DEFAULT_DIMENSION, \
                                                   EPixelFormat.PF_R8G8B8A8)

        # initialize texture for probability density function
        self.pdftexture = ue.create_transient_texture(DEFAULT_DIMENSION, DEFAULT_DIMENSION, \
                                                   EPixelFormat.PF_R8G8B8A8)

        # initialize texture with blank image
        self.texture.texture_set_data(Image.init(256, 256, Pixel.TRANSPARENT))
        self.pdftexture.texture_set_data(Image.init(256, 256, Pixel.TRANSPARENT))

        # try to load texture to draw trace to
        self.mat_valid = False
        try:
            mat = ue.load_object(MaterialInstance, "/Game/STOEC/python_graph_inst")
            pdfmat = ue.load_object(MaterialInstance, "/Game/STOEC/python_pdfgraph_inst")
        except:
            ue.log("Failed to load python_mat material instance")
            ue.print_string("Failed to load python_mat material instance")
            return
        else:
            mat.set_material_texture_parameter("Graph", self.texture)
            pdfmat.set_material_texture_parameter("Graph", self.pdftexture)
            self.mat_valid = True

    def tick(self, delta_time):
        self.server.listen()
        
if __name__ == "__main__":
    server = Server()
    while (1):
        server.listen()
    server.stop()