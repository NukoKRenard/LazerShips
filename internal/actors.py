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
                 minSpeed=0,maxSpeed=1,maxrotatespeed = 1/10,
                 maxhealth = 1):
        ActorTemplate.__init__(self,starshipCostumes,ID)
        self.__health = maxhealth
        self.__maxhealth = maxhealth

        self.__maxspeed = maxSpeed
        self.__minspeed = minSpeed
        self.__maxrotatespeedc = maxrotatespeed

        self.__dx = 0
        self.__dy = 0
        self.__dz = 0

        self.__rp = 0
        self.__ry = 0
        self.__rr = 0

    def update(self,deltaTime):
        ActorTemplate.update(self,deltaTime)

        self.__dx -= self.__dx / 100
        self.__dy -= self.__dy / 100
        self.__dz -= self.__dz / 100

        self.__rp -= self.__rp / 100
        self.__ry -= self.__ry / 100
        self.__rr -= self.__rr / 100

        rotation = glm.mat4(1)
        if self.__rp + self.__ry + self.__rr:
            rotation *= glm.rotate(self.__maxrotatespeedc * (self.__rp + self.__ry + self.__rr), (self.__rp, self.__ry, self.__rr))
        self.rotate(rotation)
        self.translate(glm.translate((self.getRot() * glm.vec4(self.__dx, self.__dy, self.__dz, 0)).xyz))

    def pitch(self,degree):
        self.__rp += degree / 60
        if self.__rp > self.__maxrotatespeedc:
            self.__rp = self.__maxrotatespeedc
        elif self.__rp < -self.__maxrotatespeedc:
            self.__rp = -self.__maxrotatespeedc
    def yaw(self,degree):
        self.__ry += degree / 60
        if self.__ry > self.__maxrotatespeedc:
            self.__ry = self.__maxrotatespeedc
        elif self.__ry < -self.__maxrotatespeedc:
            self.__ry = -self.__maxrotatespeedc
    def roll(self,degree):
        self.__rr += degree / 60
        if self.__rr > self.__maxrotatespeedc:
            self.__rr = self.__maxrotatespeedc
        elif self.__rr < -self.__maxrotatespeedc:
            self.__rr = -self.__maxrotatespeedc

    def throttleSpeed(self,speed):
        self.__dz += speed / 100
        if self.__dz > self.__maxspeed:
            self.__dz = self.__maxspeed
        elif self.__dz < self.__minspeed:
            self.__dz = self.__minspeed
    def strafe(self,speed):
        self.__dx += speed / 60
        if self.__dx > self.__maxspeed/2:
            self.__dx = self.__maxspeed / 2
        elif self.__dx < -self.__maxspeed/2:
            self.__dx = -self.__maxspeed / 2
    def hover(self,speed):
        self.__dy += speed / 60
        if self.__dy > self.__maxspeed/2:
            self.__dy = self.__maxspeed / 2
        elif self.__dy < -self.__maxspeed/2:
            self.__dy = -self.__maxspeed / 2

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
    #

class AIShip(StarShipTemplate):
    def __init__(self,shipmodel,ID,team):
        StarShipTemplate.__init__(self,shipmodel,ID)
        self.__team = team
        self.__target = self.__team.getRandomEnemy()
        self.__recklessness = random.uniform(-.3,.3)

    def update(self,deltaTime):
        StarShipTemplate.update(self,deltaTime)
        targetexists = False
        for enemyteam in self.__team.getEnemies():
            if enemyteam.shipInTeam(self.__target):
                targetexists = True

        if (not self.__target) or (not targetexists):
            self.__target = self.__team.getRandomEnemy()

        enemyexists = False
        for enemyteam in self.__team.getEnemies():
            if enemyteam.shipInTeam(self.__target):
                enemyexists = True
        if not self.__target:
            enemyexists = False

        if enemyexists and self.__target.getHealth()/2 < (self.getHealth()+self.__recklessness):
              pass

        elif self.__target.getHealth()/2 > (self.getHealth()+self.__recklessness):
            self.pitch(random.uniform(-1,1))
            self.yaw(random.uniform(-1,1))
            self.roll(random.uniform(-1,1))
            self.throttleSpeed(1)
        else:
            self.__target = self.__team.getRandomShip()
