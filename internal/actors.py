"""
10/26/2024
This file holds code for actors. Each actor holds a prop (called a costume) which is what is rendered to the screen.
Actors are dynamic with behaviors. Like a starship with an AI pilot, or a game object,
actors effect the flow of the game.
"""

import glm
from math import *


class ActorTemplate:
    def __init__(self,costume,startMatrix=glm.mat4(1)):
        print(costume)
        self.costume = costume
        self.__position = glm.vec4(0,0,0,1) * startMatrix
        self.__direction = glm.normalize(glm.vec4(0,0,1,0) * startMatrix)
        self.__up = glm.normalize(glm.vec4(0,1,0,0) * startMatrix)

        self.costume.objMatrix = startMatrix
    def moveWithMatrix(self,matrix):
        self.__position = self.__position * matrix
        self.__direction = glm.normalize(self.__direction * matrix)
        self.__up = glm.normalize(self.__up * matrix)

        self.costume.objMatrix *= matrix

    def getCostumeData(self):
        return self.costume

    def getPosition(self):
        return self.__position
    def getDirection(self):
        return self.__direction
    def getUp(self):
        return self.__up

    def update(self):
        pass

class StarShipTemplate(ActorTemplate):
    def __init__(self, starshipCostume,minSpeed=0,maxSpeed=1/60,startMatrix = glm.mat4(1)):
        ActorTemplate.__init__(self,starshipCostume,startMatrix)

        self.speedMin = minSpeed
        self.speedMax = maxSpeed
        self.speed = minSpeed
        self.ID = self.costume.ID

    def update(self,deltaTime):
        movevector = glm.vec4(0,0,self.speed*deltaTime,0)
        movevectorrotated = glm.rotate(glm.translate(movevector.xyz),radians(360),self.getDirection().xyz)
        self.moveWithMatrix(movevectorrotated)