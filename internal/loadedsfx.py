import internal.props as props
import pygame

global explosion
explosion = pygame.mixer.Sound("sfx/Explosion.wav")

global avaxEngine
avaxEngine = ["sfx/"+file for file in ("AvaxShipAccelerate.mp3","AvaxShipDecelerate.mp3")]