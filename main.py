"""
Skyler O'Bonsawin
10/19/2024
This file is the entry point of the program. It holds the Program() class which is how the game is run.
"""
#Import and Initialize
import pygame
pygame.init()
pygame.mixer.init(channels=500,buffer=10000)
import glm
import copy
import random

import internal.globalvariables as progvar

import internal.camera as camera
import internal.props as props
import internal.actors as actors
import internal.methods as datatypes

class Program:
    def __init__(self):


        #Display
        #Creates the pygame window.
        screen = pygame.display.set_mode((0,0), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN)
        cameraoffset = glm.translate((0,7,-15))
        pygame.mouse.set_visible(False)

        # Entities
        # Creates a camera actor, and tells it to draw directly to the pygame window. (Setting rendertarget to 0 means it will draw directly to the screen instead of a texture.)
        #Note: At this point the display is already made, we are just creating an entity to render to it.
        progvar.CAMERA = camera.ShipCamera(90, screen.get_size(), rendertarget=0, offset=cameraoffset)

        #The progvar.ASSETS list is used for drawing to the screen. If something needs to be shown on screen it needs to be here.
        progvar.ASSETS = []

        #The progvar.SHIPS list is used for detecting colissions. It is faster to use a seperate list than to check every item in the draw list.
        progvar.SHIPS = []

        #Populates the map with asteroids
        for i in range(200):
            mp = progvar.MAPSIZE // 2
            asteroid = actors.Asteroid()

            scale = (.2+glm.vec3(random.random(),random.random(),random.random())*.8)*30
            asteroid.setScale(glm.scale(scale))
            asteroid.setpos(glm.translate(glm.vec3(random.randint(-mp, mp), random.randint(-mp, mp), random.randint(-mp, mp))))

            progvar.ASSETS.append(asteroid)
            progvar.ASTEROIDS.append(asteroid)

        #Teams are how the ships allignthemselves and choose their enemies. Each ship has a team, which is how they pick targets,
        avaxTeam = datatypes.Team("Avax", [], [],(.5, 1, 1))
        tx01Team = datatypes.Team("TX-01", [], [],(1, 1, .5))

        # These two functions cause the teams to add the other to their enemy list. This allows all of the ships in the team to start fighting.
        avaxTeam.declareWar(tx01Team)
        tx01Team.declareWar(avaxTeam)

        #Creates a skybox
        progvar.SKYBOX = props.Skybox("skyboxes/mapskybox")
        progvar.ASSETS.append(progvar.SKYBOX)

        #Adds the camera to the assets list (They are treated the same as actors in game code and need to be updated in order to render.)
        progvar.ASSETS.append(progvar.CAMERA)

        #Adds a number of ships for each team
        for i in range(20):
            ship = actors.AIShip([props.Model("levelobjects/AvaxShip.obj",
                                    "levelobjects/texturedata/AvaxShipBase.png",
                                     "levelobjects/texturedata/AvaxShipGlowMap.png")],str(i)+"avax",avaxTeam)
            avaxTeam.addToTeam(ship)
            progvar.ASSETS.append(ship)
        for i in range(20):
            ship = actors.AIShip([props.Model("levelobjects/Starship.obj",
                                    "levelobjects/texturedata/StarshipColourMapRed.png",
                                     "levelobjects/texturedata/StarshipRoughnessGlowmap.png")],str(i)+"tx01",tx01Team)
            tx01Team.addToTeam(ship)
            progvar.ASSETS.append(ship)

        # This checks all of the assets in the progvar.ASSETS list, and if it is a ship type it adds them to the progvar.SHIPS list
        for asset in progvar.ASSETS:
            if isinstance(asset, actors.AIShip):
                progvar.SHIPS.append(asset)

        # Randomly sets the position of all of the ships.
        for ship in progvar.SHIPS:
            mp = progvar.MAPSIZE//2
            ship.setpos(glm.translate(glm.vec3(random.randint(-mp, mp), random.randint(-mp, mp), random.randint(-mp, mp))))
        #Adds the player:
        player = avaxTeam.getRandomMember()
        playeroutofboundstext = props.ScreenSpaceLabel("Placeholdertext",size=100)
        progvar.ASSETS.append(playeroutofboundstext)
        playerhealthbar = actors.healthBar(ship=player)
        playerhealthbar.setpos(glm.translate((0,-.7,-1.0)))
        progvar.ASSETS.append(playerhealthbar)
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
        avaxcount = props.ScreenSpaceLabel(str(len(avaxTeam.getAllMembers())),size=100,color=(0,200,200))
        avaxcount.setpos(glm.translate((.5,.5,-1.0)))
        progvar.ASSETS.append(avaxcount)

        tx01count = props.ScreenSpaceLabel(str(len(tx01Team.getAllMembers())),size=100,color=(200,200,0))
        tx01count.setpos(glm.translate((-.5, .5, -1.0)))
        progvar.ASSETS.append(tx01count)

        #Action
        #Assign key variables
        playerthrottle = .5
        greyscaleamtlastframe = 0
        clock = pygame.time.Clock()
        userhasquit = False
        explosionshakeamt = 0
        winconditionrealised = False

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
                    if event.key == pygame.K_x:
                        player.switchtarget(1)
                    elif event.key == pygame.K_z:
                        player.switchtarget(-1)
                    elif event.key == pygame.K_c:
                        player.targetAttacker()
                if event.type == pygame.MOUSEWHEEL:
                    playerthrottle += event.y*(1/60)
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
                    playerhealthbar.attachToShip(player)
                    progvar.CAMERA.attachToShip(player)
                    greyscaleamtlastframe = 0
                    player.heal(-1)
                    player.disableAI()
            #Refresh

            if player:
                playertarget = player.getTarget()
                if playertarget:
                    targetloc = progvar.CAMERA.getPerspectiveMatrix() * progvar.CAMERA.getWorldMatrix() * playertarget.getPos() * glm.vec4(0, 0, 0, 1)
                    targetloc = targetloc/targetloc.w

                    targetloc.x = targetloc.x if abs(targetloc.x) <= 1 else targetloc.x/abs(targetloc.x)
                    targetloc.x *= progvar.CAMERA.getAspectRatio()
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
                if ship.getVelocity().z > ship.getMaxSpeed():
                    raise Exception(f"Error: {ship.getName()} is above the max speed.")

            avaxcount.changeText(str(len(avaxTeam.getAllMembers())))
            tx01count.changeText(str(len(tx01Team.getAllMembers())))

            #Changes the image to greyscale if the player is out of bounds.
            if player and glm.length((player.getPos() * glm.vec4(0, 0, 0, 1))) > progvar.MAPSIZE:
                if greyscaleamtlastframe < 0:
                    greyscaleamtlastframe = 0
                greyscaleamtlastframe += progvar.DELTATIME/(60*10)

                playeroutofboundstext.setpos(glm.translate((0,0,-1)))
                playeroutofboundstext.changeText(f"You are leaving the area, return within {10-int(greyscaleamtlastframe*10)}s")

                #Kills the player if they have been out of bounds for 10 or more seconds.
                if greyscaleamtlastframe >= 1:
                    player.damage(player.getMaxHealth())
            else:
                playeroutofboundstext.setpos(glm.translate((0,0,1)))
                if greyscaleamtlastframe > 1:
                    greyscaleamtlastframe = 1
                greyscaleamtlastframe -= progvar.DELTATIME/(60*3)

            progvar.CAMERA.setPostProssGreyscale(greyscaleamtlastframe*2)

            #Updates all of the objects
            for asset in progvar.ASSETS:
                if issubclass(type(asset),actors.Actor):
                    asset.update()

                if isinstance(asset,actors.ExplosionEffect) and player:
                    if glm.distance(player.getPos()*glm.vec4(0,0,0,1),asset.getPos()*glm.vec4(0,0,0,1)):
                        explosionshakeamt += (asset.getShockwaveScale()/glm.distance(player.getPos()*glm.vec4(0,0,0,1),asset.getPos()*glm.vec4(0,0,0,1)))*.00

            progvar.PLAYER = player

            explosionshakeamt -= .002 if explosionshakeamt > .002 else -explosionshakeamt
            explosionshakeamt = explosionshakeamt if explosionshakeamt < 0.1 else 0.1

            progvar.CAMERA.setPostProssShake(explosionshakeamt*.1)

            #Checks loose and win conditions every frame. If one is met it sets the condition.
            if len(tx01Team.getAllMembers()) < 1 and not winconditionrealised:
                winconditionrealised = True

                pygame.mixer.music.load("sfx/SongWin.mp3")
                pygame.mixer.music.play()

                wincondtext = props.ScreenSpaceLabel("YOU WIN!",(255,255,0),500)
                wincondtext.setpos(glm.translate((0,0,-1)))
                progvar.ASSETS.append(wincondtext)
            elif len(avaxTeam.getAllMembers()) < 1 and not winconditionrealised:
                winconditionrealised = True

                pygame.mixer.music.load("sfx/SongLoss.mp3")
                pygame.mixer.music.play()

                wincondtext = props.ScreenSpaceLabel("YOU LOOSE!",(255,0,0),500)
                wincondtext.setpos(glm.translate((0,0,-1)))
                progvar.ASSETS.append(wincondtext)

            #This function loops through all of the objects in the progvar.ASSETS list and draws them with their drawObj() function
            pygame.display.flip()






Program()