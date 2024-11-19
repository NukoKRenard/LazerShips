"""
10/27/2024
This file contains datatypes for the game.
"""

import random
import glm

#The team class for all of the ships
class Team:
    def __init__(self,teamname,ships,enemyteams,teamcolor):
        self.__name = teamname
        self.__ships = list(ships)
        self.__enemies = list(enemyteams)
        self.__color = glm.vec3(teamcolor)

    #Tests if the inputted ship is part of a team.
    def shipInTeam(self,ship):
        return ship in self.__ships

    def getRandomShip(self):
        if self.__ships:
            if len(self.__ships) > 1:
                return self.__ships[random.randint(0, len(self.__ships) - 1)]

            else:
                return self.__ships[0]

    def removeFromTeam(self,target):
        try:
            self.__ships.remove(target)
        except:
            print(f"{target} not in team {self}...")

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
                enemy = self.__enemies[0].getRandomShip()
            return enemy
        return None
    def getTeamColor(self):
        return self.__color
    def getAllEnemies(self):
        totalenemies = []
        for enemyteam in self.__enemies:
            totalenemies.extend(enemyteam.getAllMembers())
        return totalenemies
    def getAllMembers(self):
        return self.__ships