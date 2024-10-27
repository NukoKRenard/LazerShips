"""
10/27/2024
This file contains datatypes for the game.
"""

class Team:
    def __init__(self,teamname,enemyteamnames):
        self.name = teamname
        self.enemyteams = enemyteamnames