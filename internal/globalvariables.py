"""
Skyler O'Bonsawin
11/14/2024
This file holds global variables to be used between the different modules.
"""
import pygame
pygame.init()

global MAPSIZE
MAPSIZE = 2000

#A list of objects that need to be drawn to the screen.
global ASSETS
ASSETS = []
#All ship objects that need to be calculated.
global SHIPS
SHIPS = []

global MODELDATA
MODELDATA = {}

global SUNPOS
SUNPOS = (0.993271,-0.00976281,0.115382)

#Static objects are divided into chunks in order to make calculations easier. This allows objects to only compare with objects in the same chunk.
global ASTEROIDS
ASTEROIDS = []

global PLAYER
PLAYER = None

#The current skybox that displays around the scene.
global SKYBOX
SKYBOX = None
#The DELTATIME variable is used to change speeds on framerate. It allows for continuity in the case of lag.
global CAMERA
CAMERA = None

global DELTATIME
DELTATIME = 1

global AIAMNESIA
AIAMNESIA = 20

global AITARGETINGINNACURACY
AITARGETINGINNACURACY = .3

global SHIPLOCKMAXDOT
SHIPLOCKMAXDOT = .90

global WEAPONRANGE
WEAPONRANGE = 1000