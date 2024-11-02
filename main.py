"""
10/19/2024
This file is the entry point of the program. It holds the Program() class which is how the game is run.
"""

#Import and Initialize
import pygame
from OpenGL.GL import *
import numpy
import glm
from math import *
import copy

import internal.camera as camera
import internal.props as props
import internal.actors as actors
import internal.datatypes as datatypes

class Program:
    def __init__(self):
        pygame.init()

        #Display
        self.maincam = camera.ShipCamera(45)

        #Entities
        self.assets = []
        starship = props.Model("levelobjects/AvaxInterceptor.obj",
                               "levelobjects/texturedata/AvaxInterceptorColourMap.png",
                               "levelobjects/texturedata/AvaxInterceptorGlowMap.png", "avaxship-costume")
        self.assets.append(props.Skybox("skyboxes/spaceSkybox0", "level-skybox"))
        self.assets.append(
            actors.StarShipTemplate([copy.deepcopy(starship)],"commander tuvok")
        )
        self.maincam.attachToShip(self.assets[1])

        avaxTeam = datatypes.Team("Avax",{},{})
        tx01Team = datatypes.Team("TX-01",{},{})

        avaxTeam.declareWar(tx01Team)
        tx01Team.declareWar(avaxTeam)

        #Action
        #Assign key variables
        self.deltaTime = 1/60
        pygame.mouse.set_visible(False)
        self.__clock = pygame.time.Clock()
        self.userhasquit = False

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
            #self.assets[1].throttleSpeed(1)
            self.assets[1].pitch(5)

            #Refresh
            self.assets[1].throttleSpeed(1)
            for asset in self.assets:
                if asset.getIsActor():
                    asset.update(self.deltaTime)


            #Clears the screen for drawing
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            #Updates the cameras position based on userinput
            #NOTE as of this stage userinput is crude. Movement directions to not account for the look direction.
            self.maincam.updateCamera(self.deltaTime)
            #This function loops through all of the objects in the prop list and draws them with their drawObj() function
            self.maincam.renderScene(self.assets)
            pygame.display.flip()






Program()