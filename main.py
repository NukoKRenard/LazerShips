"""
10/19/2024
This file is the entry point of the program. It holds the Program() class which is how the game is run.
"""

import pygame
from OpenGL.GL import *
import numpy
import glm
from math import *

import internal.camera as camera
import internal.props as props

class Program:
    def __init__(self):
        pygame.init()
        self.deltaTime = 1/60
        pygame.mouse.set_visible(False)
        self.__clock = pygame.time.Clock()
        self.models = []
        self.userhasquit = False
        self.maincam = camera.Camera(45)

        #Loads actors into a list of objects to be drawn to the screen.
        self.models.append(props.Model("levelobjects/AvaxInterceptor.obj", "levelobjects/texturedata/AvaxInterceptorColourMap.png", "ship-model"))
        self.models.append(props.Skybox("skybox","space-skybox"))

        #This is an error colour to show if something was not dran, this should ideally never be seen on the screen.
        glClearColor(1.0, 0.0, 1.0, 1)

        while not self.userhasquit:
            events = pygame.event.get()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            #The code below rotates the object in accordance with delta time, it has been disabled for debugging
            #self.models[0].objMatrix *= glm.rotate((1/60)*self.deltaTime,(0,1,0))

            for event in events:
                if event.type == pygame.QUIT:
                    self.userhasquit = True
                    break

            #Updates the cameras position based on userinput
            #NOTE as of this stage userinput is crude. Movement directions to not account for the look direction.
            self.maincam.updateCamera(self.deltaTime)
            #This function loops through all of the objects in the prop list and draws them with the drawObj() function
            self.maincam.renderScene(self.models)

            pygame.display.flip()
            self.__clock.tick(60)
            if (self.__clock.get_fps()/60) != 0:
                self.deltaTime = 1/(self.__clock.get_fps()/60)
            else:
                self.deltaTime = 0






Program()