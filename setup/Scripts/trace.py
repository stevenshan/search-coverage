import unreal_engine as ue

from unreal_engine import FColor, FLinearColor

from unreal_engine.enums import EBlendMode, EPixelFormat

import os

from unreal_engine.classes import MaterialInstance
from unreal_engine.classes import Actor

import math
import random
from Pixel_Image import Pixel, Image, DEFAULT_DIMENSION

class Trace:
    def __init__(self, uobject, obj, width = DEFAULT_DIMENSION, \
                 height = DEFAULT_DIMENSION, pixel = Pixel.TRANSPARENT):
                 
        # get camera width
        cameraDim = uobject.mapCapture.get_property('OrthoWidth')
        
        self.uobject = uobject
        self.width = width
        self.height = height
        self.view_width = cameraDim
        self.view_height = cameraDim
        self.obj = obj

        position = obj.get_actor_location()
        self.init_i = position[0]
        self.init_j = position[1]

        self.buffer = Image(width, height, pixel)

    def get_pixel_coord(self, coord):
        i = (0.5 - (coord[0] - self.init_i) / self.view_height) * self.height
        j = ((coord[1] - self.init_j) / self.view_width + 0.5) * self.width
        return round(i), round(j)

    def update(self):
        position = self.obj.get_actor_location()
        coord = self.get_pixel_coord(position)
        self.buffer.set_pixel(coord[0], coord[1], Pixel.BLACK)

class traceClass:

    def begin_play(self):

        self.width = DEFAULT_DIMENSION
        self.height = DEFAULT_DIMENSION 

        self.i = 0
        self.j = 0

        firstAgentFound = False 
        self.firstAgent = None
        self.followCamera = None
        self.stoecActor = None

        # make list of agents
        self.clients = []
        for x in self.uobject.all_objects():
            try:
                name = x.get_name()
            except:
                pass
            else:
                if name == "SuvCarPawn_C_0":
                    self.clients.append(Trace(self.uobject, x))
                    if not firstAgentFound:
                        firstAgentFound = True
                        self.firstAgent = x 
                elif name == "BP_FlyingPawn_C_0":
                    self.clients.append(Trace(self.uobject, x))
                    if not firstAgentFound:
                        firstAgentFound = True
                        self.firstAgent = x 
                elif name == "followCamera_56":
                    self.followCamera = x
                elif name == "stoec_actor_612":
                    self.stoecActor = x

        if self.stoecActor != None and self.firstAgent != None:
            target_location = self.firstAgent.get_actor_location()
            origin_location = self.stoecActor.get_actor_location()
            target_location.z = origin_location.z
            self.stoecActor.set_actor_location(target_location)

        self.texture = ue.create_transient_texture(self.width, self.height, \
                                                   EPixelFormat.PF_R8G8B8A8)

        # try to load texture to draw trace to
        self.valid = False
        try:
            mat = ue.load_object(MaterialInstance, "/Game/STOEC/python_mat_inst")
        except:
            ue.log("Failed to load python_mat material instance")
            ue.print_string("Failed to load python_mat material instance")
            return
        else:
            mat.set_material_texture_parameter("Graph", self.texture)
            self.valid = True

    def tick(self, delta_time):
        if not self.valid: return

        if self.firstAgent != None and self.followCamera != None:
            target_location = self.firstAgent.get_actor_location()
            self.followCamera.set_actor_location(target_location)

        for client in self.clients:
            client.update()
            self.texture.texture_set_data(client.buffer.image)
