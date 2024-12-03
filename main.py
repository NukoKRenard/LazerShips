"""
10/19/2024
This file is the entry point of the program. It holds the Program() class which is how the game is run.
"""
#Import and Initialize
import pygame
import pyglm.glm as glm
import copy
import random

import internal.globalvariables as progvar

import internal.camera as camera
import internal.props as props
import internal.actors as actors
import internal.datatypes as datatypes

class Program:
    def __init__(self):
        pygame.init()

        #Display
        #Creates the pygame window.
        screen = pygame.display.set_mode((1080,720), pygame.OPENGL | pygame.DOUBLEBUF)


        cameraoffset = glm.translate((0,10,-20))
        #Creates a camera actor, and tells it to draw directly to the pygame window. (Setting rendertarget to 0 means it will draw directly to the screen instead of a texture.)
        progvar.CAMERA = camera.ShipCamera(90,screen.get_size(),rendertarget=0,offset=cameraoffset)

        # Entities
        #The progvar.ASSETS list is used for drawing to the screen. If something needs to be shown on screen it needs to be here.
        progvar.ASSETS = []
        #The progvar.SHIPS list is used for detecting colissions. It is faster to use a seperate list than to check every item in the draw list.
        progvar.SHIPS = []

        #Teams are how the ships allignthemselves and choose their enemies. Each ship has a team, which is how they pick targets,
        avaxTeam = datatypes.Team("Avax", [], [],(.5, 1, 1))
        tx01Team = datatypes.Team("TX-01", [], [],(1, 1, .5))

        # These two functions cause the teams to add the other to their enemy list. This allows all of the ships in the team to start fighting.
        avaxTeam.declareWar(tx01Team)
        tx01Team.declareWar(avaxTeam)

        blueteam_ship = props.Model("levelobjects/Starship.obj",
                               "levelobjects/texturedata/StarshipColourMapBlue.png",
                               "levelobjects/texturedata/StarshipRoughnessGlowmap.png")
        redteam_ship = props.Model("levelobjects/Starship.obj",
                                    "levelobjects/texturedata/StarshipColourMapRed.png",
                                    "levelobjects/texturedata/StarshipRoughnessGlowmap.png")
        #Creates a skybox
        progvar.SKYBOX = props.Skybox("skyboxes/spaceSkybox0")
        progvar.ASSETS.append(progvar.SKYBOX)

        #Adds the camera to the assets list (They are treated the same as actors in game code and need to be updated in order to render.)
        progvar.ASSETS.append(progvar.CAMERA)

        #Adds a number of ships for each team
        for i in range(20):
            ship = actors.AIShip([copy.deepcopy(blueteam_ship)],str(i)+"avax",avaxTeam,progvar.SHIPS)
            avaxTeam.addToTeam(ship)
            progvar.ASSETS.append(ship)
        for i in range(20):
            ship = actors.AIShip([copy.deepcopy(redteam_ship)],str(i)+"tx01",tx01Team,progvar.SHIPS)
            tx01Team.addToTeam(ship)
            progvar.ASSETS.append(ship)

        # This checks all of the assets in the progvar.ASSETS list, and if it is a ship type it adds them to the progvar.SHIPS list
        for asset in progvar.ASSETS:
            if isinstance(asset, actors.AIShip):
                progvar.SHIPS.append(asset)

        # Randomly sets the position of all of the ships.
        for ship in progvar.SHIPS:
            ship.setpos(glm.translate(glm.vec3(random.randint(-500, 500), random.randint(-500, 500), random.randint(-500, 500))))

        #Adds the player:
        player = avaxTeam.getRandomMember()
        progvar.CAMERA.attachToShip(player)
        if player:
            player.disableAI()

        #Adds the targeting recitle (and the two supporting images)
        crosshairenabled = pygame.image.load("levelobjects/sprites/crosshairenabled.png")
        crosshairdisabled = pygame.image.load("levelobjects/sprites/crosshairdisabled.png")
        crosshairreversed = pygame.image.load("levelobjects/sprites/crosshairreverse.png")
        crosshair = props.ScreenSpaceSprite(crosshairenabled)
        progvar.ASSETS.append(crosshair)

        crosshair.setScale(glm.scale((.1,.1,.1)))

        #Adds the text showing the player count per team
        avaxcount = props.ScreenSpaceLabel(str(len(avaxTeam.getAllMembers())),size=100,color=(0,0,200))
        avaxcount.setpos(glm.translate((.5,.5,-1.0)))
        progvar.ASSETS.append(avaxcount)

        tx01count = props.ScreenSpaceLabel(str(len(tx01Team.getAllMembers())),size=100,color=(200,0,0))
        tx01count.setpos(glm.translate((-.5, .5, -1.0)))
        progvar.ASSETS.append(tx01count)

        #Adds text telling the player to return if they try to leave the map
        leavemaptimetext = props.ScreenSpaceLabel("Placeholdertext", size=100)

        #Action
        #Assign key variables
        playerthrottle = .5
        playerleftmaptime = 0
        playerenteredmaptime = 0
        clock = pygame.time.Clock()
        userhasquit = False

        #Loop
        while not userhasquit:
            #Time
            clock.tick(60)
            #This modifies the delta time variable based on the framerate,
            if (clock.get_fps() / 60) != 0:
                progvar.DELTATIME = 1 / (clock.get_fps() / 60)
            else:
                progvar.DELTATIME = 1

            # Deltatime can NOT ever equal zero or it would cause huge problems.
            if progvar.DELTATIME == 0:
                progvar.DELTATIME = 1

            #Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    userhasquit = True
                    break
                elif event.type == pygame.KEYDOWN and player:
                    if event.key == pygame.K_EQUALS:
                        player.switchtarget(1)
                    elif event.key == pygame.K_MINUS:
                        player.switchtarget(-1)
                if event.type == pygame.MOUSEWHEEL:
                    playerthrottle += event.y*(1/60)

            if player:
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    player.fire()

                if pygame.mouse.get_pressed()[0]:
                    player.roll(-1)
                elif pygame.mouse.get_pressed()[2]:
                    player.roll(1)
                if playerthrottle > 1:
                    playerthrottle = 1
                elif playerthrottle < -1:
                    playerthrottle = -1
                player.throttleSpeed(playerthrottle*player.getMaxSpeed()-player.getVelocity().z)
                border = 200
                mousepos = ((glm.vec2(pygame.mouse.get_pos()) / glm.vec2(progvar.CAMERA.getScreenDimensions()))-.5)*5
                mousepospx = [pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]]
                if mousepospx[0] <= border*progvar.CAMERA.getAspectRatio():
                    mousepospx[0] = border*progvar.CAMERA.getAspectRatio()
                elif mousepospx[0] >= progvar.CAMERA.getScreenDimensions()[0]-(border*progvar.CAMERA.getAspectRatio()):
                    mousepospx[0] = (progvar.CAMERA.getScreenDimensions()[0]-(border*progvar.CAMERA.getAspectRatio()))
                if mousepospx[1] <= border:
                    mousepospx[1] = border
                elif mousepospx[1] >= progvar.CAMERA.getScreenDimensions()[1]-border:
                    mousepospx[1] = progvar.CAMERA.getScreenDimensions()[1]-border
                pygame.mouse.set_pos(mousepospx)

                player.yaw(-mousepos.x-player.getYawVelocity())
                player.pitch(-mousepos.y-player.getPitchVelocity())
            if player not in progvar.SHIPS:
                player = avaxTeam.getRandomMember()
                if player:
                    progvar.CAMERA.attachToShip(player)
                    player.disableAI()
            #Refresh
            for asset in progvar.ASSETS:
                if issubclass(type(asset),actors.Actor):
                    asset.update()

            playertarget = player.getTarget()
            if player and playertarget:
                targetloc = progvar.CAMERA.getPerspectiveMatrix() * progvar.CAMERA.getWorldMatrix() * playertarget.getPos() * glm.vec4(0, 0, 0, 1)
                targetloc = targetloc/targetloc.w

                targetloc.x = targetloc.x if abs(targetloc.x) <=1 else targetloc.x/abs(targetloc.x)
                targetloc.y = targetloc.y if abs(targetloc.y) <= 1 else targetloc.y/abs(targetloc.y)
                crosshair.setpos(glm.translate((targetloc.x,targetloc.y,-1)))

                if player.isLocked():
                    if crosshair.getImage() != crosshairenabled:
                        crosshair.changeImage(crosshairenabled)

                elif player.getTargetDot() >= 0:
                    if crosshair.getImage() != crosshairdisabled:
                        crosshair.changeImage(crosshairdisabled)

                elif crosshair.getImage() != crosshairreversed:
                    crosshair.changeImage(crosshairreversed)

            for ship in progvar.SHIPS:
                if ship.getVelocity().z > 5:
                    raise Exception(f"Error: {ship.getName()} is above the max speed.")

            avaxcount.changeText(str(len(avaxTeam.getAllMembers())))
            tx01count.changeText(str(len(tx01Team.getAllMembers())))

            #Changes the image to greyscale if the player is out of bounds.
            if player and glm.length((player.getPos() * glm.vec4(0, 0, 0, 1))) > progvar.MAPSIZE:
                playerenteredmaptime = 0
                if not playerleftmaptime:
                    playerleftmaptime = (pygame.time.get_ticks()*60*progvar.DELTATIME)
                    if leavemaptimetext not in progvar.ASSETS:
                        progvar.ASSETS.append(leavemaptimetext)

                #Displays a message warning them to return.
                playertime = int((pygame.time.get_ticks()*60*progvar.DELTATIME) - playerleftmaptime)
                countdown = 10 - playertime
                countdown = countdown if countdown > 0 else 0
                leavemaptimetext.changeText(f"Return to the fight. You have {countdown} seconds!")

                #Kills the player if they are out of bounds for too long.
                if 10 - playertime < 0:
                    player.damage(1)

                progvar.CAMERA.setPostProssGreyscale(((pygame.time.get_ticks()*60*progvar.DELTATIME)-playerleftmaptime)/10)
            else:
                playerleftmaptime = 0
                if not playerenteredmaptime:
                    if leavemaptimetext in progvar.ASSETS:
                        progvar.ASSETS.remove(leavemaptimetext)
                    playerenteredmaptime = (pygame.time.get_ticks()*60*progvar.DELTATIME)

                progvar.CAMERA.setPostProssGreyscale(1 - ((pygame.time.get_ticks()*60*progvar.DELTATIME) - playerenteredmaptime) / 10)

            #This function loops through all of the objects in the progvar.ASSETS list and draws them with their drawObj() function
            pygame.display.flip()






Program()