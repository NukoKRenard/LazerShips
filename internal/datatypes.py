"""
10/27/2024
This file contains datatypes for the game.
"""

import random

class Team:
    def __init__(self,teamname,ships,enemyteams):
        self.__name = teamname
        self.__ships = set(ships)
        self.__enemies = set(enemyteams)

    def shipInTeam(self,ship):
        return ship in self.__ships

    def getRandomShip(self):
        return self.__ships[random.random(0,len(self.__ships)-1)]

    def removeFromTeam(self,target):
        self.__ships.remove(target)

    def addToTeam(self,target):
        self.__ships.add(target)

    def getName(self):
        return self.__name

    def declareWar(self,enemy):
        self.__enemies.add(enemy)

    def declarePeace(self,formerenemy):
        self.__enemies.remove(formerenemy)