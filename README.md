# Starship Shooting games
This is a game I made from scratch using the OpenGL graphics engine and pygame.

(All models, textures, sound effects, music, and code are made by and are property of Skyler O'Bonsawin please ask before using them in your own projects.)

## Running the game (Windows)
To run the game double click the ```run.bat``` file in the foldr

Please ensure a python 3 interpreter is present on the computer and is a part of path.

**The following packages are required by the game to run. If not installed the ```run.bat``` file will attempt to install them automatically.**
* numpy
* pyglm
* pyopengl
* pygame

## Running the game (Linux & MacOS)
If you want to run the game on Linux or MacOS then you will have to install python3 and all of the dependancies (listed above) manually.

To install python packages manually, use the terminal with the command:
```pip install <package-name>```
or
```python -m pip install <package-name>```

After installing everyting, open the terminal, set the common directory as the folder where the main.py script is located and then run the script using the python exe in that same terminal window.
```cd <Path to the game's folder> ```
```python main.py```

## Controlls:

Mouse X            - controlls yaw

Mouse Y            - controlls pitch

Mouse Button Left  - Roll Left

Mouse Button Right - Roll right

Mouse Scrollwheel  - Controlls Throttle




Key Z              - Select Previous target

Key X              - Select Next Target

Key C              - Select Attacker

Space Bar          - Fire Lazer




## HUD (Heads Up Display):
Green box                     - Locked and ready to fire.

Grey box with an X through it - Indicates location of target, as well as your inability to fire due to not being pointed at the target or your distance from it.

Grey cross                    - Indicates that your target is behind you.

Cyan Numbers   - Indicates how many teammates you have left

Orange Numbers - Indicates the number of enemy ships

Blue Bar       - This is your health bar.

## Goal:
Your goal is to destroy all enemy ships.

Your only way to heal is to destroy an enemy.

Avoid crashing into asteroids or other ships.

Avoid going out of bounds.

# Have fun!
