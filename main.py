"""
10/19/2024
This file is the entry point of the program. It holds the Program() class which is how the game is run.
"""
import time

#Import and Initialize

import internal.globalvariables as progvar

import pygame
import math
from OpenGL.GL import *
import numpy
import glm
from math import *
import copy
import random

import internal.camera as camera
import internal.props as props
import internal.actors as actors
import internal.datatypes as datatypes

class Program:
    def __init__(self):
        pygame.init()

        #Display
        #The camera handles the screen and drawing functions.
        self.maincam = camera.ShipCamera(90)
        progvar.CAMERA = self.maincam

        # Entities
        #The self.assets list is used for drawing to the screen. If something needs to be shown on screen it needs to be here.
        self.assets = []
        progvar.ASSETS = self.assets
        #The self.ships list is used for detecting colissions. It is faster to use a seperate list than to check every item in the draw list.
        self.ships = []
        progvar.SHIPS = self.ships

        #Teams are how the ships allignthemselves and choose their enemies. Each ship has a team, which is how they pick targets,
        self.avaxTeam = datatypes.Team("Avax", {}, {},(.5, 1, 1))
        self.tx01Team = datatypes.Team("TX-01", {}, {},(1, 1, .5))

        blueteam_ship = props.Model("levelobjects/Starship.obj",
                               "levelobjects/texturedata/StarshipColourMapBlue.png",
                               "levelobjects/texturedata/StarshipRoughnessGlowmap.png", "blueteam-costume")
        redteam_ship = props.Model("levelobjects/Starship.obj",
                                    "levelobjects/texturedata/StarshipColourMapRed.png",
                                    "levelobjects/texturedata/StarshipRoughnessGlowmap.png", "redteam-costume")
        #Creates a skybox
        progvar.SKYBOX = props.Skybox("skyboxes/spaceSkybox0", "level-skybox")
        #self.assets.append(progvar.SKYBOX)

        #Adds a number of ships for each team
        for i in range(1):
            ship = actors.AIShip([copy.deepcopy(blueteam_ship)],str(i)+"avax",self.avaxTeam,self.ships)
            self.avaxTeam.addToTeam(ship)
            self.assets.append(ship)
        for i in range(1):
            ship = actors.AIShip([copy.deepcopy(redteam_ship)],str(i)+"tx01",self.tx01Team,self.ships)
            self.tx01Team.addToTeam(ship)
            self.assets.append(ship)


        #These two functions cause the teams to add the other to their enemy list. This allows all of the ships in the team to start fighting.
        self.avaxTeam.declareWar(self.tx01Team)
        self.tx01Team.declareWar(self.avaxTeam)

        #Adds the player:
        self.player = self.avaxTeam.getRandomMember()
        self.maincam.attachToShip(self.player)
        self.player.disableAI()

        #Adds the targeting recitle (and the two supporting images)
        crosshairenabled = pygame.image.load("levelobjects/sprites/crosshairenabled.png")
        crosshairdisabled = pygame.image.load("levelobjects/sprites/crosshairdisabled.png")
        self.crosshair = props.ScreenSpaceSprite(crosshairenabled)
        self.assets.append(self.crosshair)

        self.crosshair.setScale(glm.scale((.1,.1,.1)))

        #This checks all of the assets in the self.assets list, and if it is a ship type it adds them to the self.ships type
        #NOTE: This will be updated to include player controlled ships when those are implimented.
        for asset in self.assets:
            if isinstance(asset,actors.AIShip):
                self.ships.append(asset)

        #Randomly sets the position of all of the ships.
        for ship in self.ships:
            if self.player == ship:
                ship.setpos(glm.translate((0,0,0)))
            else:
                ship.setpos(glm.translate((0,0,100)))
            #ship.setpos(glm.translate(glm.vec3(random.randint(-200,200),random.randint(-200,200),random.randint(-200,200))))

        #Action
        #Assign key variables
        pygame.mouse.set_visible(False)
        self.__clock = pygame.time.Clock()
        self.userhasquit = False
        #This variable is only for debugging. It will be removed before release.

        #Loop
        while not self.userhasquit:
            #Time
            self.__clock.tick(60)
            #This modifies the delta time variable based on the framerate,
            if (self.__clock.get_fps() / 60) != 0:
                progvar.DELTATIME = 1 / (self.__clock.get_fps() / 60)
            else:
                progvar.DELTATIME = 1

            # Deltatime can NOT ever equal zero or it would cause huge problems.
            if progvar.DELTATIME == 0:
                progvar.DELTATIME = 1

            #Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.userhasquit = True
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_EQUALS:
                        self.player.switchtarget(1)
                    elif event.key == pygame.K_MINUS:
                        self.player.switchtarget(-1)
                    print(f"Target switched to: {self.player.getTarget().getID()}")
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                self.player.fire()

            if self.player not in self.ships:
                self.player = self.avaxTeam.getRandomMember()
                self.maincam.attachToShip(self.player)
                self.player.disableAI()

            #Refresh
            for asset in self.assets:
                if asset.getIsActor():
                    asset.update()

            targetloc = self.maincam.getPerspectiveMatrix()*self.maincam.getWorldMatrix()*self.player.getTarget().getPos()*glm.vec4(0,0,0,1)
            targetloc = glm.vec3(targetloc)/targetloc.z
            print(targetloc.xyz)
            self.crosshair.setpos(glm.translate((targetloc.x,targetloc.z,-1.0)))

            #Clears the screen for drawing
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            #Updates the cameras position based on userinput
            #NOTE as of this stage userinput is crude. Movement directions to not account for the look direction.
            self.maincam.updateCamera()
            #This function loops through all of the objects in the self.assets list and draws them with their drawObj() function
            self.maincam.renderScene(self.assets)
            pygame.display.flip()






Program()