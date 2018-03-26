# telnet program example
import socket, string, sys
import os
import re

import matplotlib.pyplot as plt

import pickle, struct

class Simulation:
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

    # display a matplotlib plot
    def displayPlot(self, fig):
        data = (((0, None),(1, "figure")), ("displayGraph", fig.canvas.buffer_rgba()))
        data = pickle.dumps(data)
        msg = struct.pack('>I', len(data)) + data
        self.sock.sendall(msg)

        data = re.findall("[0-9]+", self.sock.recv(4096).decode("utf-8"))
