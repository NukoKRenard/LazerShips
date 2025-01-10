"""
Skyler O'Bonsawin
10/27/2024
This file contains datatypes for the game. These datatypes have no physical representation, they are just used to grab objects.
"""

import random
import glm
import pygame

import internal.globalvariables as progvar

#A team is a collection of ships. A ship's team can be used to get allies, and enemies.
class Team:
    def __init__(self,teamname : str,ships : list,enemyteams : list, teamcolor : tuple[float,float,float]):
        self.__name = teamname
        self.__ships = list(ships)
        self.__enemies = list(enemyteams)
        self.__color = glm.vec3(teamcolor)

    #Tests if the inputted ship is part of a team.
    def shipInTeam(self,ship):
        return ship in self.__ships
    #Gets a random member of the team.
    def getRandomMember(self):
        if self.__ships:
            if len(self.__ships) > 1:
                return self.__ships[random.randint(0, len(self.__ships) - 1)]

            else:
                return self.__ships[0]
    #Removes a ship from the team.
    def removeFromTeam(self,target):
        if target in self.__ships:
            self.__ships.remove(target)
    #Adds a ship to the team
    def addToTeam(self,target):
        self.__ships.append(target)
    #Returns the teamname.
    def getName(self):
        return self.__name
    #Adds a team to this team's list of enemies.
    def declareWar(self,enemy):
        self.__enemies.append(enemy)
    #Removes a team from this team's liswt of enemies.
    def declarePeace(self,formerenemy):
        self.__enemies.remove(formerenemy)
    #Returns a list of enemy teams.
    def getEnemies(self):
        return self.__enemies
    #Gets a random enemy from a random enemy team.
    def getRandomEnemy(self):
        if self.__enemies:
            enemy = None
            if len(self.__enemies) > 1:
                enemy = self.__enemies[random.randint(0,len(self.__enemies)-1)].getRandomMember()

            else:
                enemy = self.__enemies[0].getRandomMember()
            return enemy
        return None
    #Returns the team colour in RGB format.
    def getTeamColor(self):
        return self.__color
    #Gets all of the enemies from all of the enemy teams.
    def getAllEnemies(self):
        totalenemies = []
        for enemyteam in self.__enemies:
            totalenemies.extend(enemyteam.getAllMembers())
        return totalenemies
    #Gets all of the members of the team.
    def getAllMembers(self):
        return self.__ships

    def notifyOfDistress(self,caller):
        for ship in self.__ships:
            if random.random() <= 0.15 and ship.getHealth() > (ship.getMaxHealth()/4.0)*3.0 and ship.getAI():
                ship.setTarget(caller.getTarget())
