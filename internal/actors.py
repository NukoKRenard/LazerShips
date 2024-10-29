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
    def __init__(self,costumes,ID,startMatrix=glm.mat4(1)):
        self.costumes = costumes
        self.__position = glm.vec4(0,0,0,1) * startMatrix
        self.__direction = glm.normalize(glm.vec4(0,0,1,0) * startMatrix)
        self.__up = glm.normalize(glm.vec4(0,1,0,0) * startMatrix)
        self.__ID = ID

    def getID(self):
        return self.__ID

    def getIsActor(self):
        return True

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
    def moveWithMatrix(self,matrix,coordinatecenter=None):
        if coordinatecenter == None:
            coordinatecenter = self.__position
        self.__position = self.__position * matrix
        self.__direction = glm.normalize(self.__direction * matrix)
        self.__up = glm.normalize(self.__up * matrix)

        for costume in self.costumes:
            if costume.getIsActor():
                costume.moveWithMatrix(matrix,coordinatecenter)
            else:
                costumeobjmatrixprev = copy.copy(costume.objMatrix)
                costume.objMatrix *= matrix
                print((costumeobjmatrixprev * glm.vec4(0, 0, 0, 1)))

    def getCostumeData(self):
        return self.costumes

    def getPosition(self):
        return self.__position
    def getDirection(self):
        return self.__direction
    def getUp(self):
        return self.__up

    def update(self,deltaTime):
        for costume in self.costumes:
            if costume.getIsActor():
                costume.update(deltaTime)

class StarShipTemplate(ActorTemplate):
    def __init__(self, starshipCostumes,ID,minSpeed=0,maxSpeed=1/20,maxrotatespeed = 1/60,startMatrix = glm.mat4(1)):
        ActorTemplate.__init__(self,starshipCostumes,ID,startMatrix)

        self.speedMin = minSpeed
        self.speedMax = maxSpeed

        self.maxRotationSpeed = maxrotatespeed

        self.forwardSpeed = minSpeed
        self.strafeSpeed = 0
        self.hoverSpeed = 0

        self.pitchSpeed = 0
        self.yawSpeed = 0
        self.rollSpeed = 0

    def flightControll(self,thrustvector,rotationvector):
        self.strafeSpeed += thrustvector[0]*(1/(self.speedMax*10000))
        self.hoverSpeed += thrustvector[1]*(1/(self.speedMax*10000))
        self.forwardSpeed += thrustvector[2]*(1/(self.speedMax*10000))

        if self.forwardSpeed > self.speedMax:
            self.forwardSpeed = self.speedMax
        elif self.forwardSpeed < self.speedMin:
            self.forwardSpeed = self.speedMin

        if self.strafeSpeed > self.speedMax / 3:
            self.strafeSpeed = self.speedMax / 3
        elif self.strafeSpeed < -self.speedMax / 3:
            self.strafeSpeed = -self.speedMax / 3

        if self.hoverSpeed > self.speedMax / 3:
            self.hoverSpeed = self.speedMax / 3
        elif self.hoverSpeed < -self.speedMax / 3:
            self.hoverSpeed = -self.speedMax / 3

        self.pitchSpeed += rotationvector[0]*(1/(self.maxRotationSpeed*10000))
        self.yawSpeed += rotationvector[1]*(1/(self.maxRotationSpeed*10000))
        self.rollSpeed += rotationvector[2]*(1/(self.maxRotationSpeed*10000))

        if self.pitchSpeed > self.maxRotationSpeed:
            self.pitchSpeed = self.maxRotationSpeed
        elif self.pitchSpeed < -self.maxRotationSpeed:
            self.pitchSpeed = -self.maxRotationSpeed

        if self.yawSpeed > self.maxRotationSpeed:
            self.yawSpeed = self.maxRotationSpeed
        elif self.yawSpeed < -self.maxRotationSpeed:
            self.yawSpeed = -self.maxRotationSpeed

        if self.rollSpeed > self.maxRotationSpeed:
            self.rollSpeed = self.maxRotationSpeed
        elif self.rollSpeed < -self.maxRotationSpeed:
            self.rollSpeed = -self.maxRotationSpeed

    def update(self,deltaTime):
        keys = pygame.key.get_pressed()

        rotationOffset = glm.rotate(radians(360), self.getDirection().xyz)
        speedRotation = glm.rotate(self.pitchSpeed,(1,0,0)) * rotationOffset
        self.moveWithMatrix(speedRotation)
        speedRotation = glm.rotate(self.yawSpeed, (0, 1, 0)) * rotationOffset
        self.moveWithMatrix(speedRotation)
        speedRotation = glm.rotate(self.rollSpeed, (0, 0, 1)) * rotationOffset
        self.moveWithMatrix(speedRotation)

        speedTranslation = glm.translate(
            (glm.vec4(self.strafeSpeed*deltaTime, self.hoverSpeed*deltaTime, self.forwardSpeed*deltaTime, 0) * rotationOffset).xyz)
        self.moveWithMatrix(speedTranslation)

        if self.strafeSpeed > 0:
            self.strafeSpeed -= 1/(self.speedMax*100000)
        elif self.strafeSpeed < 0:
            self.strafeSpeed += (1/(self.speedMax*100000))

        if self.hoverSpeed > 0:
            self.hoverSpeed -= 1/(self.speedMax*100000)
        elif self.hoverSpeed < 0:
            self.hoverSpeed += (1/(self.speedMax*100000))

        if self.pitchSpeed > 0:
            self.pitchSpeed -= 1/(self.maxRotationSpeed*100000)
        elif self.pitchSpeed < 0:
            self.pitchSpeed += (1/(self.maxRotationSpeed*100000))

        if self.yawSpeed > 0:
            self.yawSpeed -= 1/(self.maxRotationSpeed*100000)
        elif self.yawSpeed < 0:
            self.yawSpeed += (1/(self.maxRotationSpeed*100000))

        if self.rollSpeed > 0:
            self.rollSpeed -= 1/(self.maxRotationSpeed*100000)
        elif self.rollSpeed < 0:
            self.rollSpeed += (1/(self.maxRotationSpeed*100000))

        for costume in self.costumes:
            if costume.getIsActor():
                costume.update(deltaTime)