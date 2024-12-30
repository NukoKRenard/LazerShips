import internal.props as props
import pygame

global explosion
explosion = pygame.mixer.Sound("sfx/Explosion.mp3")

global avaxShip
avaxShip = ["sfx/" + file for file in ("AvaxShipAccelerate.mp3", "AvaxShipDecelerate.mp3", "LazerFiring.mp3")]