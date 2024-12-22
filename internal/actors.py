"""
10/26/2024
This file holds code for actors. Each actor holds a prop (called a costume) which is what is rendered to the screen.
Actors are dynamic with behaviors. Like a starship with an AI pilot, or a game object,
actors effect the flow of the game.
"""
import copy
from os import times

import internal.globalvariables as progvar
import glm
import pygame
import random
import internal.props as props
import internal.datatypes as datatypes

from math import *



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
                parentMatrix : glm.mat4(1) = glm.mat4(1)
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

    def update(self,parentMatrix : glm.mat4 = glm.mat4(1)) -> None:
        for costume in self.__costumes:
            if issubclass(type(costume),Actor):
                costume.update(parentMatrix)

    def removefromgame(self) -> None:
        if self in progvar.ASSETS:
            progvar.ASSETS.remove(self)
    def getCostumes(self) -> list:
        return self.__costumes
    def addCostume(self, costume) -> None:
        if isinstance(costume,props.Prop) or isinstance(costume,Actor):
            self.__costumes.append(costume)
        else:
            raise Exception(f"Invalid costume appended to actor: {self}")

#This is a template for a starship type. Has some basic movement functions
class StarShipTemplate(Actor):
    def __init__(self,
                 starshipCostumes,
                 minSpeed : float =0 ,
                 maxSpeed : float =3 ,
                 maxrotatespeed : float= 1/9,
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

    def update(self, parentMatrix : glm.mat4 = glm.mat4(1)) -> None:
        Actor.update(self, parentMatrix)

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
        self.__dz += (speed / 100)*progvar.DELTATIME*self.getMaxSpeed()
        if self.__dz > self.__maxspeed:
            self.__dz = self.__maxspeed
        elif self.__dz < self.__minspeed:
            self.__dz = self.__minspeed
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

    def damage(self,points : float,attacker : Actor | None = None) -> bool:
        if points < 0:
            raise Exception(f"Starship recieved {points} damage, damage points can not be negative.")
        self.__health -= points
        if self.__health <= 0:
            self.removefromgame()
            progvar.ASSETS.append(ExplosionEffect(self.getPos(),self.getRot(),self.getScale()))
            return True
        return False

    def heal(self,points : float) -> None:
        if points < 0 and points != -1:
            raise Exception(f"Starship recieved {points} healing, healing points can not be negative.")
        self.__health += points

        #If the health value is negative 1 it will fully heal the ship.
        if points == -1:
            self.__health = self.__maxhealth

        if self.__health >= self.__maxhealth:
            self.__health = self.__maxhealth
    def getHealth(self) -> float:
        return self.__health
    def getMaxHealth(self):
        return self.__maxhealth

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
    def __init__(self,shipmodel,Name : str,team : datatypes.Team):
        StarShipTemplate.__init__(self,shipmodel)
        self.__team = team
        self.__target = self.__team.getRandomEnemy()
        self.__recklessness = random.uniform(0,1)
        self.__lastfiretime = 0
        self.__AI = True
        self.__firing = False
        self.__enemyDot = 1
        self.__hasLock = False
        self.__name = Name
        self.__lazerSfx = sfx3D(progvar.LAZERSFX,True)
        self.addCostume(self.__lazerSfx)
        self.__lastAttacker = None
        self.__distressUsed = False

        self.__lazer = props.Lazer((self.getPos()*glm.vec4(0,0,0,1)).xyz,(self.getPos()*glm.vec4(0,0,0,1)).xyz,self.__team.getTeamColor())
        progvar.ASSETS.append(self.__lazer)

    def update(self, parentMatrix : glm.mat4 = glm.mat4(1)) -> None:
        StarShipTemplate.update(self, parentMatrix)

        if self.__firing:
            self.__lazer.setvisible()
            self.__lazerSfx.play()
        else:
            self.__lazer.setnotvisible()
            self.__lazerSfx.stop()
        self.__firing = False

        if not self.__target or self.__target not in progvar.SHIPS:
            self.__target = self.__team.getRandomEnemy()
            self.__timesincelastfire = pygame.time.get_ticks()

        if self.__target:
            self.__enemyDot = glm.dot(glm.normalize(((glm.inverse(self.getPos())*self.__target.getPos())*glm.vec4(0,0,0,1)).xyz),(self.getRot()*glm.vec4(0,0,1,0)).xyz)
            targetdist = glm.distance((self.getPos()*glm.vec4(0,0,0,1)).xyz,(self.__target.getPos()*(0,0,0,1)).xyz)
            if self.__enemyDot >= progvar.SHIPLOCKMAXDOT and targetdist < progvar.WEAPONRANGE:
                self.__hasLock = True
            else:
                self.__hasLock = False

            if self.__AI and self.__target:
                # Control's the AI's target choices, and replaces it with a new one if needed.
                if (self.__lastfiretime - (pygame.time.get_ticks())) / 60 > progvar.AIAMNESIA:
                    self.__target = self.__team.getRandomEnemy()
                    self.__timesincelastfire = pygame.time.get_ticks()

                #Decides weither or weither to not fire on the targeted ship
                if self.isLocked():
                    self.fire()
                    self.__lastfiretime = pygame.time.get_ticks()

                #Checks for collisions with other ships
                collidevector = None
                for ship in progvar.SHIPS:
                    if isinstance(ship,AIShip) and ship.getPos() != self.getPos():
                        itemdist = glm.distance((ship.getPos()*glm.vec4(0,0,0,1)).xyz,(self.getPos()*glm.vec4(0,0,0,1)).xyz)
                        if itemdist < 20:
                            self.damage(self.getMaxHealth())
                            ship.damage(ship.getMaxHealth())
                            break

                        elif itemdist < (100*((self.getVelocity().z+ship.getVelocity().z)*.5 if self.getVelocity().z > 1 else 1))-self.__recklessness*20:
                            itempos = glm.normalize(glm.inverse(glm.inverse(self.getPos())*ship.getPos())*glm.vec4(0,0,0,1)).xyz

                            if collidevector:
                                collidevector += itempos
                            else:
                                collidevector = itempos

                #Movement heiarchy
                # If you are nearly out of the map boundary return back to the map
                # Otherwise if there is a colission imminent avoid it.
                # Otherwise if your target is chasing you do evasive maneuvers
                # Otherwise chase your target.
                if glm.length((self.getPos()*glm.vec4(0,0,0,1)).xyz) > progvar.MAPSIZE-100 or not self.__target:
                    self.goToPos(glm.vec3(0,0,0))
                #elif glm.dot((glm.inverse(self.__target.getPos())*self.getPos()*glm.vec4(0,0,0,1)).xyz,(self.__target.getRot()*glm.vec4(0,0,1,0)).xyz) > .9 and glm.dot((glm.inverse(self.getPos())*self.__target.getPos()*glm.vec4(0,0,0,1)).xyz,(self.getRot()*glm.vec4(0,0,1,0)).xyz) <= 0:
                #    self.goToPos((self.getPos()*glm.vec4(random.random(),random.random(),random.random(),1.0)).xyz)
                elif collidevector:
                    self.goToPos((self.getPos()*glm.vec4(collidevector,1)).xyz)
                elif self.__target:
                    self.goToPos((self.__target.getPos()*glm.vec4(0,0,0,1)).xyz)

    def goToPos(self, pos):
        relativepos = glm.vec4((glm.inverse(self.getPos())*glm.vec4(pos,1)).xyz,0)
        localdir = glm.normalize(glm.inverse(self.getRot())*relativepos)
        thrustvec = glm.normalize(localdir.xy + (-.5+glm.vec2(random.random(),random.random()))*2*(progvar.AITARGETINGINNACURACY))

        self.pitch(-thrustvec.y+self.getPitchVelocity())
        self.yaw(thrustvec.x-self.getYawVelocity())
        self.roll(thrustvec.x-self.getRollVelocity())

        self.throttleSpeed(1)



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
    def setTarget(self, target) -> None:
        if target:
            self.__target = target
    def getTarget(self) -> Actor:
        return self.__target

    def fire(self) -> None:
        self.__firing = True
        if self.__target:

            targetpos = (self.__target.getPos()*glm.vec4(0,0,0,1))
            self.__lazer.setpos(start=(self.getPos() * glm.vec4(0, 0, 0, 1)).xyz)

            if self.isLocked():
                self.__lazer.setpos(end=(self.__target.getPos() * glm.vec4(0, 0, 0, 1)).xyz)
                if self.__target.damage(.001*progvar.DELTATIME,self):
                    self.__target = self.__team.getRandomEnemy()
                    self.heal(self.getMaxHealth()/2)

            else:
                self.__lazer.setpos(end=((self.getPos()*glm.vec4(0,0,0,1))+(self.getRot()*glm.vec4(0,0,100,0))).xyz)
        else:
            self.__lazer.setpos(end=((self.getPos() * glm.vec4(0, 0, 0, 1)) + (self.getRot() * glm.vec4(0, 0, 100, 0))).xyz)


    def damage(self,points : float ,attacker : Actor | None = None) -> bool:
        if attacker:
            self.__lastAttacker = attacker
        if self.__AI:
            self.targetAttacker()
        if StarShipTemplate.damage(self,points,attacker):
            self.__team.removeFromTeam(self)
            self.__lazer.removefromgame()

        if self.getHealth() < self.getMaxHealth()/2.0 and self.__target == progvar.PLAYER and not self.__distressUsed:
            self.__team.notifyOfDistress(self)
            self.__distressUsed = True

            return True
        return False
    def targetAttacker(self):
        if self.__lastAttacker in progvar.SHIPS:
            self.__target = self.__lastAttacker
        else:
            self.__lastAttacker = None

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
    def getAI(self):
        return self.__AI

class healthBar(Actor):
   def __init__(self, color : tuple[int,int,int] = (0,200,200), ship : AIShip = None):
       self.__target = ship

       self.__color = color
       self.__image = pygame.surface.Surface((1000,100))
       pygame.draw.rect(self.__image,(100,100,100),self.__image.get_rect(),border_radius=50)
       rect = pygame.Rect(10,10,980,80)
       pygame.draw.rect(self.__image, self.__color, rect, border_radius=50)
       self.__image.set_colorkey((0,0,0))

       self.__sprite = props.ScreenSpaceSprite(self.__image)
       Actor.__init__(self,[self.__sprite])

       if self.__target:
           self.__lastframehealth = self.__target.getHealth()

   def attachToShip(self, ship : AIShip) -> None:
       self.__lastframehealth = ship.getHealth()
       self.__target = ship

   def changeColor(self, color : tuple[int,int,int]) -> None:
       self.__color = color
   def update(self, parentMatrix : glm.mat4 = glm.mat4(1)):
       Actor.update(self,parentMatrix)

       if self.__target:
           health = self.__target.getHealth()
           if health != self.__lastframehealth:
               self.__lastframehealth = health

               self.__image.fill((0,0,0))

               self.__image = pygame.surface.Surface((1000, 100))
               pygame.draw.rect(self.__image, (100, 100, 100), self.__image.get_rect(), border_radius=50)
               rect = pygame.Rect(10, 10, 980*health, 80)
               pygame.draw.rect(self.__image, self.__color, rect, border_radius=50)
               self.__image.set_colorkey((0, 0, 0))

               self.__sprite.changeImage(self.__image)

class ExplosionEffect(Actor):
    def __init__(self,position : glm.mat4, rotation : glm.mat4, scale : glm.mat4, lifetime : float =30):
        Actor.__init__(self, [])
        self.__starttime = pygame.time.get_ticks()
        self.__lifetime = lifetime

        self.__shockwave = props.Model("levelobjects/TexturePlane.obj",
                                    "levelobjects/texturedata/ShockWaveTexture.png",
                                    "levelobjects/texturedata/ShockWaveGlowMap.png")
        self.__shockwave.setScale(glm.scale((1,1,1))*scale)
        self.__shockwave.setrot(rotation)
        self.__shockwave.setpos(position)
        self.addCostume(self.__shockwave)

        self.__sound = sfx3D(progvar.EXPLOSIONSFX)
        self.addCostume(self.__sound)

        self.setpos(position)
        self.__sound.play()

    def update(self, parentMatrix : glm.mat4 = glm.mat4(1)):
        Actor.update(self, parentMatrix*self.getPos())

        timesincebegin = (pygame.time.get_ticks()-self.__starttime)/60

        self.__shockwave.resize(glm.scale((1.2, 1.2, 1.2)))
        self.__shockwave.setopacity(.5 - (timesincebegin / self.__lifetime) * .5)

        if timesincebegin > self.__lifetime:
            self.removefromgame()

    def getShockwaveScale(self) -> float:
        return glm.length(self.__shockwave.getScale()*glm.vec4(1,1,1,0))/3

class sfx3D(Actor):
    def __init__(self,sound : pygame.mixer.Sound, looping : bool = False):
        self.__sfx = sound
        self.__looping = looping
        self.__sfxchannel = None
        self.__playingnow = False

        Actor.__init__(self,[])

    def update(self, parentMatrix : glm.mat4 = glm.mat4(1)):
        worldpos = parentMatrix * self.getPos()
        Actor.update(self,worldpos)


        playerdist = glm.distance((worldpos*glm.vec4(0,0,0,1)).xyz,(progvar.CAMERA.getPos()*glm.vec4(0,0,0,1)).xyz)

        self.__sfx.set_volume(1/(playerdist/100) if playerdist != 0 else 1)
        if self.__sfxchannel:
            if self.__looping and self.__playingnow and not self.__sfxchannel.get_busy():
                self.__sfxchannel = self.__sfx.play()
            elif not self.__sfxchannel.get_busy():
                self.__playingnow = False

    def play(self):
        if not self.__playingnow:
            self.__sfxchannel = self.__sfx.play()
            self.__playingnow = True

    def stop(self):
        self.__sfx.stop()
        self.__playingnow = False