"""
11/14/2024
This file holds global variables to be used between the different modules.
"""
import math
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
SHIPLOCKMAXDOT = .95

global WEAPONRANGE
WEAPONRANGE = 700

global EXPLOSIONSFX
EXPLOSIONSFX = pygame.mixer.Sound("sfx/Explosion.wav")

global LAZERSFX
LAZERSFX = pygame.mixer.Sound("sfx/LazerFiring.wav")