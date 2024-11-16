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
        self.assets.append(progvar.SKYBOX)

        #Adds a number of ships for each team
        for i in range(100):
            ship = actors.AIShip([copy.deepcopy(blueteam_ship)],str(i)+"avax",self.avaxTeam,self.ships)
            self.avaxTeam.addToTeam(ship)
            self.assets.append(ship)
        for i in range(100):
            ship = actors.AIShip([copy.deepcopy(redteam_ship)],str(i)+"tx01",self.tx01Team,self.ships)
            self.tx01Team.addToTeam(ship)
            self.assets.append(ship)


        #These two functions cause the teams to add the other to their enemy list. This allows all of the ships in the team to start fighting.
        self.avaxTeam.declareWar(self.tx01Team)
        self.tx01Team.declareWar(self.avaxTeam)

        #This checks all of the assets in the self.assets list, and if it is a ship type it adds them to the self.ships type
        #NOTE: This will be updated to include player controlled ships when those are implimented.
        for asset in self.assets:
            if isinstance(asset,actors.AIShip):
                self.ships.append(asset)

        #Randomly sets the position of all of the ships.
        for ship in self.ships:
            ship.setpos(glm.translate(glm.vec3(random.randint(-200,200),random.randint(-200,200),random.randint(-200,200))))

        self.maincam.attachToShip(self.ships[random.randint(0,len(self.ships)-1)])

        #Action
        #Assign key variables
        #The self.deltaTime variable is used to change speeds on framerate. It allows for continuity in the case of lag.
        self.deltaTime = 1/60
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
                self.deltaTime = 1 / (self.__clock.get_fps() / 60)
            else:
                self.deltaTime = 1

            #Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.userhasquit = True
                    break
            events = pygame.event.get()

            #Refresh
            for asset in self.assets:
                if asset.getIsActor():
                    asset.update(self.deltaTime)

            if self.maincam.getShip() not in self.ships:
                self.maincam.attachToShip(self.ships[random.randint(0,len(self.ships)-1)])

            largestdist = 0
            for ship in self.ships:
                shipdist = glm.length((ship.getPos()*glm.vec4(0,0,0,1)).xyz)
                largestdist = shipdist if shipdist > largestdist else largestdist
            print(largestdist)

            #Clears the screen for drawing
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            #Updates the cameras position based on userinput
            #NOTE as of this stage userinput is crude. Movement directions to not account for the look direction.
            self.maincam.updateCamera(self.deltaTime)
            #This function loops through all of the objects in the self.assets list and draws them with their drawObj() function
            self.maincam.renderScene(self.assets)
            pygame.display.flip()






Program()