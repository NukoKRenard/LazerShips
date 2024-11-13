"""
10/19/2024
This file is the entry point of the program. It holds the Program() class which is how the game is run.
"""

#Import and Initialize
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
        self.maincam = camera.ShipCamera(90)

        # Entities
        self.assets = []
        self.ships = []

        avaxTeam = datatypes.Team("Avax", {}, {})
        tx01Team = datatypes.Team("TX-01", {}, {})

        blueteam_ship = props.Model("levelobjects/Starship.obj",
                               "levelobjects/texturedata/StarshipColourMapBlue.png",
                               "levelobjects/texturedata/StarshipRoughnessGlowmap.png", "blueteam-costume")
        redteam_ship = props.Model("levelobjects/Starship.obj",
                                    "levelobjects/texturedata/StarshipColourMapRed.png",
                                    "levelobjects/texturedata/StarshipRoughnessGlowmap.png", "redteam-costume")
        self.assets.append(props.Skybox("skyboxes/spaceSkybox0", "level-skybox"))
        """self.assets.append(
            actors.AIShip([copy.deepcopy(blueteam_ship)],"commander tuvok",tx01Team,self.ships)
        )"""
        #tx01Team.addToTeam(self.assets[1])

        """self.assets.append(
            actors.AIShip([copy.deepcopy(blueteam_ship)],"Commander riker",avaxTeam,self.ships)
        )"""
        #self.assets[2].setpos(glm.translate((0,0,0)))
        #avaxTeam.addToTeam(self.assets[2])
        #self.maincam.attachToShip(self.assets[1])

        for i in range(5):
            ship = actors.AIShip([copy.deepcopy(blueteam_ship)],str(i)+"avax",avaxTeam,self.ships)
            avaxTeam.addToTeam(ship)
            self.assets.append(ship)

        for i in range(5):
            ship = actors.AIShip([copy.deepcopy(redteam_ship)],str(i)+"tx01",tx01Team,self.ships)
            tx01Team.addToTeam(ship)
            self.assets.append(ship)

        avaxTeam.declareWar(tx01Team)

        tx01Team.declareWar(avaxTeam)

        for asset in self.assets:
            if isinstance(asset,actors.AIShip):
                self.ships.append(asset)

        for ship in self.ships:
            ship.setpos(glm.translate(glm.vec3(random.randint(-100,100),random.randint(-100,100),random.randint(-100,100))))

        self.maincam.attachToShip(self.ships[random.randint(0,len(self.ships)-1)])

        #Action
        #Assign key variables
        self.deltaTime = 1/60
        pygame.mouse.set_visible(False)
        self.__clock = pygame.time.Clock()
        self.userhasquit = False
        totalassets = len(self.assets)
        #Loop
        while not self.userhasquit:
            #Time
            self.__clock.tick(60)
            if (self.__clock.get_fps() / 60) != 0:
                self.deltaTime = 1 / (self.__clock.get_fps() / 60)
            else:
                self.deltaTime = 0

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

            """self.assets[2].pitch(random.uniform(-1,1))
            self.assets[2].yaw(random.uniform(-1,1))
            self.assets[2].roll(random.uniform(-1,1))
            self.assets[2].throttleSpeed(1)"""

            if len(self.assets) < totalassets:
                raise Exception(f"Error: {totalassets-len(self.assets)} assets are missing.")

            #Clears the screen for drawing
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            #Updates the cameras position based on userinput
            #NOTE as of this stage userinput is crude. Movement directions to not account for the look direction.
            self.maincam.updateCamera(self.deltaTime)
            #This function loops through all of the objects in the prop list and draws them with their drawObj() function
            self.maincam.renderScene(self.assets)
            pygame.display.flip()






Program()