import unreal_engine as ue

from unreal_engine import FColor, FLinearColor

from unreal_engine.enums import EBlendMode, EPixelFormat

import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import math

import random

class Pixel:
    TRANSPARENT = (0, 0, 0, 0)
    WHITE = (255, 255, 255, 255)
    BLACK = (0, 0, 0, 255)

class Image:
    # initialize an image as byte array with given pixel value
    @staticmethod
    def init(width, height, pixel):
        img = bytes()
        for i in range(height):
            img += bytes(list(pixel)) * width
        return img

    # return an image with pixel at (i, j) replaced with given pixel
    @staticmethod
    def replace_pixel(img, i, j, width, pixel):
        return img[:(i * width + j) * 4] + \
               bytes(list(pixel)) + \
               img[(i * width + j + 1) * 4:]

    def __init__(self, width, height, pixel = Pixel.TRANSPARENT):
        self.image = self.init(width, height, pixel)
        self.width = width
        self.height = height

    def set_pixel(self, i, j, pixel):
        if i >= 0 and i < self.height and j >= 0 and j < self.width:
            self.image = self.replace_pixel(self.image, i, j, self.width, pixel)

    def draw_line(self, coord1, coord2, pixel = Pixel.BLACK):
        # starting point of line
        i, j = coord1[0], coord1[1]

        # length of line
        dist = int(round(math.sqrt((coord2[0] - coord1[0]) ** 2 + 
                                   (coord2[1] - coord1[1]) ** 2)))

        slope = (coord2[0] - coord1[0]) / dist, (coord2[1] - coord1[1]) / dist
        # draw line
        for k in range(dist):
            self.set_pixel(round(i), round(j), pixel)
            i += slope[0]
            j += slope[1]

class Trace:
    def __init__(self, uobject, obj, width = 256, height = 256, 
                 view_width = 6000, view_height = 6000, pixel = Pixel.WHITE):
        self.uobject = uobject
        self.width = width
        self.height = height
        self.view_width = 6000
        self.view_height = 6000
        self.obj = obj

        position = obj.get_actor_location()
        self.init_i = position[0]
        self.init_j = position[1]

        self.buffer = Image(width, height, pixel)
        self.texture = ue.create_transient_texture(width, height,  \
                                                   EPixelFormat.PF_R8G8B8A8)
        self.texture.texture_set_data(self.buffer.image)
        self.texture.auto_root()

    def get_pixel_coord(self, coord):
        i = (0.5 - (coord[0] - self.init_i) / self.view_height) * self.height
        j = ((coord[1] - self.init_j) / self.view_width + 0.5) * self.width
        return round(i), round(j)

    def update(self):
        position = self.obj.get_actor_location()
        coord = self.get_pixel_coord(position)
        self.buffer.set_pixel(coord[0], coord[1], Pixel.BLACK)
        self.texture.texture_set_data(self.buffer.image)

    def draw(self):
        self.update()
        self.uobject.hud_draw_texture(self.texture, 800, 0, self.width, self.height)

class STOEC:

    def begin_play(self):

        self.component_width = 256
        self.component_height = 256 

        self.width = 512
        self.height = 512 

        for viewport_client in ue.all_viewport_clients():
            origin, size = viewport_client.get_viewport_dimensions()
            self.width = max(self.width, size[0]) 
            self.height = max(self.height, size[1])

        # set texture/plot dimensions and dpi, ensure dpi is a float !
        dpi = 72.0

        '''
        # create a new figure with the specified sizes
        fig = plt.figure(1)
        fig.set_dpi(dpi)
        fig.set_figwidth(width/dpi)
        fig.set_figheight(height/dpi)

        # plot a simple graph with a label on the y axis
        plt.plot([1, 2, 3, 4])
        plt.ylabel('some numbers')

        # draw the graph (in memory)
        fig.canvas.draw()
        
        self.buf = fig.canvas.buffer_rgba()
        #buf = self.set_pixel(buf, i, j, width, (128, 255, 255, 255))

        # copy pixels from matplotlib canvas to the texture as RGBA
        self.texture.texture_set_data(self.buf)
        '''

        self.i = 0
        self.j = 0

        # this automatically destroys the texture when self.texture dies (this is required as UE does not know about this texture object)
        self.draw_hud()

        self.clients = []
        for x in self.uobject.all_objects():
            if x.get_name() == "SuvCarPawn_C_0":
                self.clients.append(Trace(self.uobject, x))
            elif x.get_name() == "BP_FlyingPawn_C_0":
                self.clients.append(Trace(self.uobject, x))


    def draw_hud(self):

        try:
            for client in self.clients:
                client.draw()
        except:
            ue.print_string("not initiated")

        #self.buf.set_pixel(random.randint(0, self.component_height), random.randint(0, self.component_width), (0, 0, 0, 255))
        #self.trace_texture.texture_set_data(self.buf.image)

        # draw what the player pawn is seeing
        #self.uobject.hud_draw_texture(self.trace_texture, 0, 0, self.component_width, self.component_height)
