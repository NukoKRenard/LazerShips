"""
Skyler O'Bonsawin
2025/01/10
This file paths to soundfiles. This is so that they can be easily changed if needed.
"""

import internal.props as props
import pygame

global explosion
explosion = "sfx/Explosion.mp3"

global avaxShip
avaxShip = ["sfx/" + file for file in ("AvaxShipAccelerate.mp3", "AvaxShipDecelerate.mp3", "LazerFiring.mp3")]