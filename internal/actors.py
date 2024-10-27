"""
10/26/2024
This file holds code for actors. Each actor holds a prop (called a costume) which is what is rendered to the screen.
Actors are dynamic with behaviors. Like a starship with an AI pilot, or a game object,
actors effect the flow of the game.
"""

import glm
import pygame
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
    def __init__(self, starshipCostume,minSpeed=0,maxSpeed=1/20,startMatrix = glm.mat4(1)):
        ActorTemplate.__init__(self,starshipCostume,startMatrix)

        self.speedMin = minSpeed
        self.speedMax = maxSpeed
        self.forwardSpeed = minSpeed
        self.strafeSpeed = 0
        self.hoverSpeed = 0

        self.ID = self.costume.ID

    def update(self,deltaTime):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.forwardSpeed += 1/self.speedMax/10000
        elif keys[pygame.K_DOWN]:
            self.forwardSpeed  -= 1/self.speedMax/10000

        if keys[pygame.K_LEFT]:
            self.strafeSpeed += 1/(self.speedMax*100000)
        elif keys[pygame.K_RIGHT]:
            self.strafeSpeed -= 1/(self.speedMax*100000)
        else:
            self.strafeSpeed -= self.strafeSpeed/10

        if keys[pygame.K_1]:
            self.hoverSpeed -= 1/(self.speedMax*100000)
        elif keys[pygame.K_2]:
            self.hoverSpeed += 1/(self.speedMax*100000)
        else:
            self.hoverSpeed -= self.hoverSpeed/10

        print(self.hoverSpeed)

        if self.forwardSpeed > self.speedMax:
            self.forwardSpeed = self.speedMax
        elif self.forwardSpeed < self.speedMin:
            self.forwardSpeed = self.speedMin

        if self.strafeSpeed > self.speedMax/3:
            self.strafeSpeed = self.speedMax/3
        elif self.strafeSpeed < -self.speedMax/3:
            self.strafeSpeed = -self.speedMax/3

        if self.hoverSpeed > self.speedMax/3:
            self.hoverSpeed = self.speedMax/3
        elif self.hoverSpeed < -self.speedMax/3:
            self.hoverSpeed = -self.speedMax/3

        speedTranslationRotation = glm.rotate(radians(360),self.getDirection().xyz)
        speedTranslation = glm.translate((glm.vec4(self.strafeSpeed,self.hoverSpeed,self.forwardSpeed,0)*speedTranslationRotation).xyz)
        self.moveWithMatrix(speedTranslation)