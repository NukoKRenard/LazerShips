"""
10/26/2024
This file holds code for actors. Each actor holds a prop (called a costume) which is what is rendered to the screen.
Actors are dynamic with behaviors. Like a starship with an AI pilot, or a game object,
actors effect the flow of the game.
"""

import glm
import pygame
from math import *
import copy

from glm import normalize


class ActorTemplate:
    def __init__(self,costumes,ID):
        self.__translation = glm.mat4(1)
        self.__rotation = glm.mat4(1)
        self.__scale = glm.mat4(1)
        self.costumes = costumes

        self.__ID = ID

    def getID(self):
        return self.__ID

    def getIsActor(self):
        return True

    def getMatrix(self):
        return self.translation * self.rotation * self.scale

    def drawObj(self, worldMatrix, perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist,
                parentMatrix=glm.mat4(1),
                ):
        for costume in self.costumes:
            costume.drawObj(
                worldMatrix, perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist,
                parentMatrix*(self.__translation*self.__rotation*self.__scale)
            )

    def translate(self, translation):
        self.__translation *= translation
    def setpos(self, position):
        self.__translation = position
    def getPos(self):
        return self.__translation;

    def rotate(self, angle):
        self.__rotation *= angle
    def setrot(self, rotation):
        self.__rotation = rotation
    def getRot(self):
        return self.__rotation

    def resize(self, resize):
        self.__scale *= resize
    def setScale(self, size):
        self.__scale = size
    def getScale(self):
        return self.__scale

    def update(self,deltaTime):
        for costume in self.costumes:
            if costume.getIsActor():
                costume.update(deltaTime)

class StarShipTemplate(ActorTemplate):
    def __init__(self, starshipCostumes,ID,minSpeed=0,maxSpeed=1/20,maxrotatespeed = 1/60):
        ActorTemplate.__init__(self,starshipCostumes,ID)

    def flightControll(self,thrustvector,rotationvector):
        pass

    def update(self,deltaTime):
        for costume in self.costumes:
            if costume.getIsActor():
                costume.update(deltaTime)

