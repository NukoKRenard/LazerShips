"""
10/27/2024
This file contains datatypes for the game.
"""

import random

#The team class for all of the ships
class Team:
    def __init__(self,teamname,ships,enemyteams):
        self.__name = teamname
        self.__ships = list(ships)
        self.__enemies = list(enemyteams)

    #Tests if the inputted ship is part of a team.
    def shipInTeam(self,ship):
        return ship in self.__ships

    def getRandomShip(self):
        if self.__ships:
            return self.__ships[random.randint(0,len(self.__ships)-1)]

    def removeFromTeam(self,target):
        self.__ships.remove(target)

    def addToTeam(self,target):
        self.__ships.append(target)

    def getName(self):
        return self.__name

    def declareWar(self,enemy):
        self.__enemies.append(enemy)

    def declarePeace(self,formerenemy):
        self.__enemies.remove(formerenemy)

    def getEnemies(self):
        return self.__enemies

    def getRandomEnemy(self):
        if self.__enemies:
            enemy = None
            if len(self.__enemies) > 1:
                enemy = self.__enemies[random.randint(0,len(self.__enemies)-1)].getRandomShip()

            else:
                enemy = self.__enemies[random.randint(0,len(self.__enemies)-1)].getRandomShip()
            return enemy
        return None