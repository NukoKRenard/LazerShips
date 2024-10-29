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
        self.translation = glm.mat4(1)
        self.rotation = glm.mat4(1)
        self.scale = glm.mat4(1)
        self.costumes = costumes
        print(self.costumes)

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
                indexbufferlist
                ):
        for costume in self.costumes:
            costume.drawObj(
                worldMatrix, perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist
            )
    def updateChildPos(self):
        pass

    def update(self,deltaTime):
        for costume in self.costumes:
            print(self.rotation)
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

