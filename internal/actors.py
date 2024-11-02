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
import random

from pygame.transform import rotate


#This is a template for an actor type. Sets some default values.
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

#This is a template for a starship type. Has some basic movement functions
class StarShipTemplate(ActorTemplate):
    def __init__(self,
                 starshipCostumes,ID,
                 minSpeed=0,maxSpeed=1/20,maxrotatespeed = 1/60,
                 maxhealth = 1):
        ActorTemplate.__init__(self,starshipCostumes,ID)
        self.__health = maxhealth
        self.__maxhealth = maxhealth

        self.__maxspeed = maxSpeed
        self.__minspeed = minSpeed
        self.__maxrotatespeedc = maxrotatespeed

        self.dx = 0
        self.dy = 0
        self.dz = 0

        self.rp = 0
        self.ry = 0
        self.rr = 0

    def update(self,deltaTime):
        ActorTemplate.update(self,deltaTime)

        self.dx -= self.dx/100
        self.dy -= self.dy/100
        self.dz -= (self.dz-self.tdz)/100

        self.rp -= self.rp/100
        print(self.rp)
        self.ry -= self.ry/100
        self.rr -= self.rr/100

        rotation = glm.mat4(1)
        if self.rp + self.ry + self.rr:
            rotation *= glm.rotate(self.__maxrotatespeedc*(self.rp+self.ry+self.rr),(self.rp,self.ry,self.rr))
        self.rotate(rotation)
        self.translate(glm.translate((self.getRot()*glm.vec4(self.dx,self.dy,self.dz,0)).xyz))

    def pitch(self,degree):
        self.rp = degree*(1/60)
    def yaw(self,degree):
        self.ry = degree*(1/60)
    def roll(self,degree):
        self.rr = degree*(1/60)

    def throttleSpeed(self,speed):
        self.tdz = self.__minspeed+((self.__maxspeed-self.__minspeed)*speed)
        if self.tdz > self.__maxspeed:
            self.tdz = self.__maxspeed
        elif self.tdz < self.__minspeed:
            self.tdz = self.__minspeed
        print(self.tdz)
    def strafe(self,speed):
        self.dx = self.__maxspeed*.5*speed
    def hover(self,speed):
        self.dy = self.__maxspeed*.5*speed

    def damage(self,points):
        if points < 0:
            raise Exception(f"Starship recieved {points} damage, damage points can not be negative.")
        self.__health -= points
        if self.__health <= 0:
            return True
        else:
            return False
    def heal(self,points):
        if points < 0:
            raise Exception(f"Starship recieved {points} healing, healing points can not be negative.")
        self.__health += points
        if self.__health >= self.__maxhealth:
            self.__health = self.__maxhealth
    def getHealth(self):
        return self.__health

class AIShip(StarShipTemplate):
    def __init__(self,shipmodel,ID,team):
        StarShipTemplate.__init__(shipmodel,ID)
        self.__team = team
        self.__target = team
        self.__recklessness = random.random(-.3,.3)

    def update(self,deltaTime):
        StarShipTemplate.update(self,deltaTime)

        if self.__team.shipInTeam(self.__target) and self.__target.getHealth()/2 < (self.getHealth()+self.__recklessness):
            pass
        elif self.__target.getHealth()/2 > (self.getHealth()+self.__recklessness):
            self.pitch(random.uniform(-1,1))
            self.yaw(random.uniform(-1,1))
            self.roll(random.uniform(-1,1))
            self.throttleSpeed(1)
        else:
            self.__target = self.__team.getRandomShip()
