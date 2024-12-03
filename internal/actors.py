"""
10/26/2024
This file holds code for actors. Each actor holds a prop (called a costume) which is what is rendered to the screen.
Actors are dynamic with behaviors. Like a starship with an AI pilot, or a game object,
actors effect the flow of the game.
"""
import internal.globalvariables as progvar
import pyglm.glm as glm
import pygame
from typing import Union
import random
import internal.props as props
import internal.datatypes as datatypes



#This is a template for an actor type. Sets some default values.
class Actor:
    def __init__(self,costumes):
        self.__translation = glm.mat4(1)
        self.__rotation = glm.mat4(1)
        self.__scale = glm.mat4(1)
        self.__costumes = costumes

    def getMatrix(self) -> glm.mat4:
        return self.__translation * self.__rotation * self.__scale

    def drawObj(self, worldMatrix : glm.mat4, perspectiveMatrix : glm.mat4,
                shaderlist : list[int],
                vertexbufferlist : list[int],
                indexbufferlist : list[int],
                parentMatrix : glm.mat4 = glm.mat4(1)
                ) -> None:
        for costume in self.__costumes:
            costume.drawObj(
                worldMatrix, perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist,
                parentMatrix*(self.__translation*self.__rotation*self.__scale)
            )

    def translate(self, translation : glm.mat4) -> None:
        self.__translation *= translation
    def setpos(self, position : glm.mat4) -> None:
        self.__translation = position
    def getPos(self) -> glm.mat4:
        return self.__translation

    def rotate(self, angle : glm.mat4) -> None:
        self.__rotation *= angle
    def setrot(self, rotation : glm.mat4) -> None:
        self.__rotation = rotation
    def getRot(self) -> glm.mat4:
        return self.__rotation

    def resize(self, resize : glm.mat4) -> None:
        self.__scale *= resize
    def setScale(self, size : glm.mat4) -> None:
        self.__scale = size
    def getScale(self) -> glm.mat4:
        return self.__scale

    def update(self) -> None:
        for costume in self.__costumes:
            if issubclass(type(costume),Actor):
                costume.update()
    def removefromgame(self) -> None:
        if self in progvar.ASSETS:
            progvar.ASSETS.remove(self)
    def getCostumes(self):
        return self.__costumes

#This is a template for a starship type. Has some basic movement functions
class StarShipTemplate(Actor):
    def __init__(self,
                 starshipCostumes,
                 minSpeed : float =0 ,
                 maxSpeed : float =5 ,
                 maxrotatespeed : float= 1/10,
                 maxhealth : float =1
    ):
        Actor.__init__(self, starshipCostumes)
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

    def update(self) -> None:
        Actor.update(self)

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

    #Rotational components of the ship
    def pitch(self,degree : float ) -> None:
        self.__rp += (degree / 60)*progvar.DELTATIME
        if self.__rp > self.__maxrotatespeedc:
            self.__rp = self.__maxrotatespeedc
        elif self.__rp < -self.__maxrotatespeedc:
            self.__rp = -self.__maxrotatespeedc
    def yaw(self,degree : float) -> None :
        self.__ry += (degree / 60)*progvar.DELTATIME
        if self.__ry > self.__maxrotatespeedc:
            self.__ry = self.__maxrotatespeedc
        elif self.__ry < -self.__maxrotatespeedc:
            self.__ry = -self.__maxrotatespeedc
    def roll(self,degree : float ) -> None:
        self.__rr += (degree / 60)*progvar.DELTATIME
        if self.__rr > self.__maxrotatespeedc:
            self.__rr = self.__maxrotatespeedc
        elif self.__rr < -self.__maxrotatespeedc:
            self.__rr = -self.__maxrotatespeedc
        self.__rr *= progvar.DELTATIME

    def getThrottleSpeed(self) -> float:
        return self.__dz
    def getMaxSpeed(self) -> float:
        return self.__maxspeed

    #Movement functions
    def throttleSpeed(self,speed : float) -> None:
        self.__dz += (speed / 100)*progvar.DELTATIME
        if self.__dz > self.__maxspeed:
            self.__dz = self.__maxspeed
        elif self.__dz < -self.__minspeed:
            self.__dz = -self.__minspeed
    def strafe(self,speed : float) -> None:
        self.__dx += (speed / 100)*progvar.DELTATIME
        if self.__dx > self.__maxspeed/2:
            self.__dx = self.__maxspeed / 2
        elif self.__dx < -self.__maxspeed/2:
            self.__dx = -self.__maxspeed / 2
    def hover(self,speed : float) -> None:
        self.__dy += (speed / 100)*progvar.DELTATIME
        if self.__dy > self.__maxspeed/2:
            self.__dy = self.__maxspeed / 2
        elif self.__dy < -self.__maxspeed/2:
            self.__dy = -self.__maxspeed / 2

    def damage(self,points : float,attacker : Union[Actor : None] = None) -> bool:
        if points < 0:
            raise Exception(f"Starship recieved {points} damage, damage points can not be negative.")
        self.__health -= points
        if self.__health <= 0:
            self.removefromgame()
            return True
        return False

    def heal(self,points : float) -> None:
        if points < 0:
            raise Exception(f"Starship recieved {points} healing, healing points can not be negative.")
        self.__health += points
        if self.__health >= self.__maxhealth:
            self.__health = self.__maxhealth
    def getHealth(self) -> float:
        return self.__health

    def getYawVelocity(self) -> float:
        return self.__ry
    def getPitchVelocity(self) -> float:
        return self.__rp
    def getRollVelocity(self) -> float:
        return self.__rr
    def getVelocity(self) -> glm.vec3:
        return glm.vec3(self.__dx,self.__dy,self.__dz)

    def removefromgame(self) -> None:
        Actor.removefromgame(self)
        if self in progvar.SHIPS:
            progvar.SHIPS.remove(self)
        for ship in progvar.SHIPS:
            if ship.getTarget() == self:
                ship.switchtarget(1)

class AIShip(StarShipTemplate):
    def __init__(self,shipmodel,Name : str,team : datatypes.Team, shipsinplay):
        StarShipTemplate.__init__(self,shipmodel)
        self.__team = team
        self.__target = self.__team.getRandomEnemy()
        self.__recklessness = random.uniform(0,1)
        self.__allships = shipsinplay
        self.__timesincelastfire = 0
        self.__AI = True
        self.__firing = False
        self.__enemyDot = 1
        self.__hasLock = False
        self.__name = Name

        self.__lazer = props.Lazer((self.getPos()*glm.vec4(0,0,0,1)).xyz,(self.getPos()*glm.vec4(0,0,0,1)).xyz,self.__team.getTeamColor())
        progvar.ASSETS.append(self.__lazer)

    def update(self) -> None:
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

            self.__hasLock = self.__enemyDot > progvar.SHIPLOCKMAXDOT and glm.length(targetpos - (self.getPos() * glm.vec4(0, 0, 0, 1))) < 300

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

                if self.__hasLock:
                    self.fire()
                    self.__timesincelastfire = 0
                else:
                    self.__timesincelastfire += pygame.time.get_ticks()*progvar.DELTATIME
                    self.__lazer.setnotvisible()

                if self.__timesincelastfire*60 > 20:
                    self.__target = self.__team.getRandomEnemy()
                    self.__timesincelastfire = 0

    def switchtarget(self, number : int) -> bool:
        if self.__target != None:
            enemyShips = self.__team.getAllEnemies()
            enemyindex = 0
            try:
                enemyindex = enemyShips.index(self.__target)
            except:
                self.__target = self.__team.getRandomEnemy()
            try:
                enemyindex += number
                enemyindex %= len(enemyShips)-1
                self.__target = enemyShips[enemyindex]
                return True
            except:
                return False

        else:
            self.__target = self.__team.getRandomEnemy()
    def getTarget(self) -> Actor:
        return self.__target

    def fire(self) -> None:
        self.__firing = True
        if self.__target:

            targetpos = (self.__target.getPos()*glm.vec4(0,0,0,1))
            targetdir = glm.normalize(targetpos-(self.getPos()*glm.vec4(0,0,0,1)))
            selfdir = self.getRot()*glm.vec4(0,0,1,1)
            self.__lazer.setpos(start=(self.getPos() * glm.vec4(0, 0, 0, 1)).xyz)

            if glm.dot(targetdir.xyz,selfdir.xyz) > progvar.SHIPLOCKMAXDOT and glm.length(targetpos - (self.getPos() * glm.vec4(0, 0, 0, 1))) < 300:
                self.__lazer.setpos(end=(self.__target.getPos() * glm.vec4(0, 0, 0, 1)).xyz)
                if self.__target.damage(.001*progvar.DELTATIME,self):
                        self.__target = None
            else:
                self.__lazer.setpos(end=((self.getPos()*glm.vec4(0,0,0,1))+(self.getRot()*glm.vec4(0,0,100,0))).xyz)
        else:
            self.__lazer.setpos(end=((self.getPos() * glm.vec4(0, 0, 0, 1)) + (self.getRot() * glm.vec4(0, 0, 100, 0))).xyz)


    def damage(self,points : float ,attacker : Union[Actor : None] = None) -> bool:
        if attacker and self.__AI:
            self.__target = attacker
        if StarShipTemplate.damage(self,points,attacker):
            self.__team.removeFromTeam(self)
            self.__lazer.removefromgame()
            return True
        return False

    def disableAI(self) -> None:
        self.__AI = False
    def enableAI(self) -> None:
        self.__AI = True
    def isLocked(self) -> bool:
        return self.__hasLock
    def getTargetDot(self) -> float:
        return self.__enemyDot
    def getName(self) -> str:
        return self.__name