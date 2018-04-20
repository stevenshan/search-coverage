# telnet program example
import socket, string, sys
import os
import re

import matplotlib.pyplot as plt

import pickle, struct

class AirsimSimulation:
    def __init__(self):
        host = "localhost"
        port = 4001

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

    # get orthographic width of top down camera as integer
    def getOrthoWidth(self):
        data = (((0, None),), ("getOrthoWidth",))
        data = pickle.dumps(data)
        msg = struct.pack('>I', len(data)) + data
        self.sock.sendall(msg)

        data = re.findall("[0-9]+", self.sock.recv(4096).decode("utf-8"))
        return int("".join(data))

    def sendImage(self, buffer, command):
        data = (((0, None),(1, "figure")), (command, buffer))
        data = pickle.dumps(data)
        msg = struct.pack('>I', len(data)) + data
        self.sock.sendall(msg)

        return re.findall("[0-9]+", self.sock.recv(4096).decode("utf-8"))

    # display a matplotlib plot
    def displayPlot(self, rgb):
        return self.sendImage(rgb, "displayGraph")

    # display a matplotlib plot
    def displayPDF(self, rgb):
        return self.sendImage(rgb, "displayPDF")
