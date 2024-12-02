"""
10/26/2024
This file holds code for actors. Each actor holds a prop (called a costume) which is what is rendered to the screen.
Actors are dynamic with behaviors. Like a starship with an AI pilot, or a game object,
actors effect the flow of the game.
"""
import time

from OpenGL.wrapper import none_or_pass

import internal.globalvariables as progvar
from memory_profiler import profile
from pyglm import glm
import pygame
from math import *
import random
import internal.props as props

global SHIPLOCRAD
SHIPLOCRAD = .95

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
        return self.__translation

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

    def update(self):
        for costume in self.costumes:
            if costume.getIsActor():
                costume.update()
    def removefromgame(self):
        try:
            progvar.ASSETS.remove(self)
        except:
            print(f"{self} not in assets list.")

#This is a template for a starship type. Has some basic movement functions
class StarShipTemplate(ActorTemplate):
    def __init__(self,
                 starshipCostumes,ID,
                 minSpeed=0,maxSpeed=5,maxrotatespeed = 1/10,
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

    def update(self):
        ActorTemplate.update(self)

        self.__dx -= self.__dx / 100
        self.__dy -= self.__dy / 100
        self.__dz -= self.__dz / 100

        self.__rp -= self.__rp / 100
        self.__ry -= self.__ry / 100
        self.__rr -= self.__rr / 10

        rm = 0
        if self.__rp or self.__ry or self.__rr:

            rm = self.__rp if self.__rp > 0 else -self.__rp
            rm += self.__ry if self.__ry > 0 else -self.__ry
            rm += self.__rr if self.__rr > 0 else -self.__rr

        rotation = glm.rotate(self.__maxrotatespeedc * rm, (self.__rp, self.__ry, self.__rr)) if (self.__rp or self.__ry or self.__rr) else glm.mat4(1)
        self.rotate(glm.mat4(rotation))
        self.translate(glm.translate((self.getRot() * glm.vec4(self.__dx, self.__dy, self.__dz, 0)).xyz))

    def pitch(self,degree):
        self.__rp += (degree / 60)*progvar.DELTATIME
        if self.__rp > self.__maxrotatespeedc:
            self.__rp = self.__maxrotatespeedc
        elif self.__rp < -self.__maxrotatespeedc:
            self.__rp = -self.__maxrotatespeedc
    def yaw(self,degree):
        self.__ry += (degree / 60)*progvar.DELTATIME
        if self.__ry > self.__maxrotatespeedc:
            self.__ry = self.__maxrotatespeedc
        elif self.__ry < -self.__maxrotatespeedc:
            self.__ry = -self.__maxrotatespeedc
    def roll(self,degree):
        self.__rr += (degree / 60)*progvar.DELTATIME
        if self.__rr > self.__maxrotatespeedc:
            self.__rr = self.__maxrotatespeedc
        elif self.__rr < -self.__maxrotatespeedc:
            self.__rr = -self.__maxrotatespeedc
        self.__rr *= progvar.DELTATIME

    def getThrottleSpeed(self):
        return self.__dz
    def getMaxSpeed(self):
        return self.__maxspeed

    def throttleSpeed(self,speed):
        self.__dz += (speed / 100)*progvar.DELTATIME
        if self.__dz > self.__maxspeed:
            self.__dz = self.__maxspeed
        elif self.__dz < -self.__minspeed:
            self.__dz = -self.__minspeed
    def strafe(self,speed):
        self.__dx += (speed / 100)*progvar.DELTATIME
        if self.__dx > self.__maxspeed/2:
            self.__dx = self.__maxspeed / 2
        elif self.__dx < -self.__maxspeed/2:
            self.__dx = -self.__maxspeed / 2
    def hover(self,speed):
        self.__dy += (speed / 100)*progvar.DELTATIME
        if self.__dy > self.__maxspeed/2:
            self.__dy = self.__maxspeed / 2
        elif self.__dy < -self.__maxspeed/2:
            self.__dy = -self.__maxspeed / 2

    def damage(self,points,attacker=None):
        if points < 0:
            raise Exception(f"Starship recieved {points} damage, damage points can not be negative.")
        self.__health -= points
        if self.__health <= 0:
            self.removefromgame()
            return True
        return False

    def heal(self,points):
        if points < 0:
            raise Exception(f"Starship recieved {points} healing, healing points can not be negative.")
        self.__health += points
        if self.__health >= self.__maxhealth:
            self.__health = self.__maxhealth
    def getHealth(self):
        return self.__health

    def getYawVelocity(self):
        return self.__ry
    def getPitchVelocity(self):
        return self.__rp
    def getRollVelocity(self):
        return self.__rr
    def getVelocity(self):
        return glm.vec3(self.__dx,self.__dy,self.__dz)
    def removefromgame(self):
        ActorTemplate.removefromgame(self)
        try:
            progvar.SHIPS.remove(self)
        except:
            print(f"{self} not in ships list...")
        for ship in progvar.SHIPS:
            if ship.getTarget() == self:
                ship.switchtarget(1)

class AIShip(StarShipTemplate):
    def __init__(self,shipmodel,ID,team,shipsinplay):
        StarShipTemplate.__init__(self,shipmodel,ID)
        self.__team = team
        self.__target = self.__team.getRandomEnemy()
        self.__recklessness = random.uniform(0,1)
        self.__allships = shipsinplay
        self.__timesincelastfire = 0
        self.__AI = True
        self.__firing = False
        self.__enemyDot = 1
        self.__hasLock = False

        self.__lazer = props.Lazer((self.getPos()*glm.vec4(0,0,0,1)).xyz,(self.getPos()*glm.vec4(0,0,0,1)).xyz,self.__team.getTeamColor())
        progvar.ASSETS.append(self.__lazer)

    def update(self):
        StarShipTemplate.update(self)
        if not self.__firing:
            self.__lazer.setnotvisible()
        else:
            self.__lazer.setvisible()
            self.__firing = False

        if not self.__target or self.__target not in self.__team.getAllEnemies():
            self.__target = self.__team.getRandomEnemy()

        if self.__target:
            targetpos = (self.__target.getPos() * glm.vec4(0, 0, 0, 1))
            targetdir = glm.normalize((targetpos - (self.getPos() * glm.vec4(0, 0, 0, 1))).xyz)
            selfdir = self.getRot() * glm.vec4(0, 0, 1, 1)
            self.__enemyDot = glm.dot(targetdir.xyz, selfdir.xyz)

            self.__hasLock = self.__enemyDot > SHIPLOCRAD and glm.length(targetpos-(self.getPos()*glm.vec4(0,0,0,1))) < 300

            if self.__AI:
                localtargetdir = glm.inverse(self.getRot())*targetdir

                targetup = self.__target.getRot()*glm.vec4(0,1,0,0)
                localtargetup = glm.inverse(self.getRot())*targetup

                selfpos = self.getPos() * glm.vec4(0, 0, 0, 1)
                if glm.length(selfpos) > progvar.MAPSIZE:
                    targetdir = glm.normalize(-selfpos)
                    localtargetdir = glm.inverse(self.getRot())*targetdir

                # This loop detects if any ships are too close (within a radius of 50) to this ship. If so it
                # stops chasing its target and instead tries to avoid a colission
                closestshipdistance = -1
                for ship in self.__allships:
                    speeddif = (glm.dot(self.getVelocity(),ship.getVelocity())/self.getMaxSpeed())*2
                    speeddif = speeddif if speeddif > 1 else 1
                    if ship.getPos() != self.getPos():
                        shippos = ship.getPos() * glm.vec4(0, 0, 0, 1)
                        shipvec = shippos-selfpos
                        if glm.length(shipvec) < 10:
                            self.damage(1)
                            ship.damage(1)
                        colissiondetected = glm.length(shipvec) < (50*speeddif)-(10*self.__recklessness)
                        if colissiondetected and closestshipdistance == -1:
                            closestshipdistance = glm.length(shipvec)
                            targetdir = shipvec/(glm.length(shipvec))
                        elif colissiondetected and closestshipdistance != -1:
                            targetdir += shipvec/(glm.length(shipvec))
                            if glm.length(shipvec) > closestshipdistance:
                                closestshipdistance = glm.length(shipvec)

                if closestshipdistance != -1:
                    targetdir = glm.normalize(targetdir)
                    localtargetdir = glm.inverse(self.getRot()) * targetdir
                    localtargetdir = glm.vec4(-localtargetdir.x, -localtargetdir.y, -localtargetdir.z, 0)

                if closestshipdistance == -1:
                    self.yaw(localtargetdir.x-self.getYawVelocity()-random.uniform(-.3,.3))
                    self.pitch(-localtargetdir.y-self.getPitchVelocity()-random.uniform(-.3,.3))
                    self.roll(-localtargetup.x-self.getRollVelocity()-random.uniform(-.3,.3))
                    self.throttleSpeed(1)
                else:
                    self.yaw(localtargetdir.x-self.getYawVelocity())
                    self.pitch(-localtargetdir.y-self.getPitchVelocity())
                    self.roll(-localtargetup.x-self.getRollVelocity())
                    self.throttleSpeed(closestshipdistance/(40-(10*self.__recklessness)))

                if self.getPos()*self.getRot()*self.getScale()*glm.scale((2,2,2)) == self.getPos()*self.getRot()*self.getScale():
                    raise Exception(f"Error ship {self.getID()} matrix is {self.getPos()*self.getRot()*self.getScale()}")

                if self.__hasLock:
                    self.fire()
                    self.__timesincelastfire = 0
                else:
                    self.__timesincelastfire += pygame.time.get_ticks()*progvar.DELTATIME
                    self.__lazer.setnotvisible()

                if self.__timesincelastfire*60 > 20:
                    self.__target = self.__team.getRandomEnemy()
                    self.__timesincelastfire = 0

    def switchtarget(self, number):
        if self.__target != None:
            enemyShips = self.__team.getAllEnemies()
            enemyindex = 0
            try:
                enemyindex = enemyShips.index(self.__target)
            except:
                self.__target = self.__team.getRandomEnemy()
            enemyindex += number
            enemyindex %= len(enemyShips)-1
            self.__target = enemyShips[enemyindex]

        else:
            self.__target = self.__team.getRandomEnemy()
    def getTarget(self):
        return self.__target

    def fire(self):
        self.__firing = True
        if self.__target:

            targetpos = (self.__target.getPos()*glm.vec4(0,0,0,1))
            targetdir = glm.normalize(targetpos-(self.getPos()*glm.vec4(0,0,0,1)))
            selfdir = self.getRot()*glm.vec4(0,0,1,1)
            self.__lazer.setpos(start=(self.getPos() * glm.vec4(0, 0, 0, 1)).xyz)

            if glm.dot(targetdir.xyz,selfdir.xyz) > SHIPLOCRAD and glm.length(targetpos-(self.getPos()*glm.vec4(0,0,0,1))) < 300:
                self.__lazer.setpos(end=(self.__target.getPos() * glm.vec4(0, 0, 0, 1)).xyz)
                if self.__target.damage(.001*progvar.DELTATIME,self):
                        self.__target = None
            else:
                self.__lazer.setpos(end=((self.getPos()*glm.vec4(0,0,0,1))+(self.getRot()*glm.vec4(0,0,100,0))).xyz)
        else:
            self.__lazer.setpos(end=((self.getPos() * glm.vec4(0, 0, 0, 1)) + (self.getRot() * glm.vec4(0, 0, 100, 0))).xyz)


    def damage(self,points,attacker=None):
        if attacker and self.__AI:
            self.__target = attacker
        if StarShipTemplate.damage(self,points,attacker):
            self.__team.removeFromTeam(self)
            self.__lazer.removefromgame()
            return True
        return False
    def disableAI(self):
        self.__AI = False
    def enableAI(self):
        self.__AI = True
    def isLocked(self):
        return self.__hasLock
    def getTargetDot(self):
        return self.__enemyDot