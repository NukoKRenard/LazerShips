# Starship Shooting games
This is a game I made from scratch using the OpenGL graphics engine. I did not use a game engine to make this. In this game you play as a blue starship, your goal is to destroy all of the enemy (red) starships.

## Running the game
Inside of this filder there is a Run.bat file. You can run that and it would automatically set the working directory and run the game. This game comes with a preconfigured virtual environment to make running the game easier. If you would like to run this game on a different interpereter, run the batch file with the path to your interpereter. (Note, it is reccomended to use the venv that the game comes with as it has the needed packages are pre installed.)
```
Run.bat "[Path to your interpereter]"
```
The run.bat script will try running the program. If packages are missing then the Run.bat file will check which ones are missing, and install them into the python environment. (it will ask you to confim instilation before installing.) after all necisary packages have been installed it will re run the program.

## Known bugs
### 1. Starship and akybox randomly dissapear.
This is due to an issue with some of the matricies being set to only NaN values. This is due to a bad calculation somewhere that does not test the matricies before multiplyimg them. I am trying to locate the issue.

### 2. Ships coliding with each other in flight.
This is due to the nature of the movement of the ships. These ships can only move as fast as their movement constraints allow them. If I slow down the ships too much then the game wont be fun. If I speed them up too much the game will become to hard. I plan to add a check where if two ships collide it will cause them both to be destroyed.
