"""
11/14/2024
This file holds global variables to be used between the different modules.
"""
#A list of objects that need to be drawn to the screen.
global ASSETS
ASSETS = []
#All ship objects that need to be calculated.
global SHIPS
SHIPS = []
#The current skybox that displays around the scene.
global SKYBOX
SKYBOX = None
#The DELTATIME variable is used to change speeds on framerate. It allows for continuity in the case of lag.
global CAMERA
CAMERA = None
global DELTATIME
DELTATIME = 1

global MAPSIZE
MAPSIZE = 500

global SHIPLOCKMAXDOT
SHIPLOCKMAXDOT = .95