# Starship Shooting games
This is a game I made from scratch using the OpenGL graphics engine. I did not use a game engine to make this. In this game you play as a blue starship, your goal is to destroy all of the enemy (red) starships.

## Running the game
Inside of this filder there is a Run.bat file. You can run that and it would automatically set the working directory and run the game. This game comes with a preconfigured virtual environment to make running the game easier. If an error occurs when running the game, the run.bat script will try to automatically fix it, or give the user steps to fix it. **To run the game, double click the run.bat file, or run it using the terminal.**

## Known bugs

### 1. Ships coliding with each other in flight.
This is due to the nature of the movement of the ships. These ships can only move as fast as their movement constraints allow them. If I slow down the ships too much then the game wont be fun. If I speed them up too much the game will become to hard. I plan to add a check where if two ships collide it will cause them both to be destroyed.
