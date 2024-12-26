# Overview of the "Chickadee" game engine.
This document goes into detail about the game engine I designed to make this game. I call it "Chickadee" after the tiny but brave bird. 

## Global Variables
The ```globalvariables.py``` (often referred to as progvar in the code) has a number of variables shared throughout the program. They can used to store settings that can be tweaked (like the MAPSIZE), data used in functions (such as DELTATIME), or used to hold objects (such as ASSETS, SHIPS, or ASTEROIDS)
### Settings
These classes are stored in globalvariables purely so that they can be easily tweaked and changed quickly to ensure production goes smoothly.

### Data
These are either data that is used in calculations (like DELTATIME) or references to objects that are used to identify them (like MAINCAM to identify the rendering camera, or PLAYER to identify the ship that the player is playing as.)

### Storage
The most noteworthy of the storage data is ASSETS, which contains a list of all of the items that are in the game world. ASSETS is the top level of props and actors, and is what the game loops through, updates, and draws to the screen every frame. ASSETS can also be broken down into other data lists like SHIPS, or ASTEROIDS, these lists are used so that any function that loops through all the items, does not need to go through everything and check, and only loops through the proper items (like with the AIShip's collision function, it only needs to see other ships and asteroids, by only looping through these it saves time to calculate.)

## Object types
Objects are items that have a physical place in the game world whether visible or not. A Model or AIship is an example of an object, the Team class stored in ``methods.py`` is **NOT** an object due to it not having a physical place in the game scene. Objects can be of the type of Props or Actors. They can be stored in the ASSETS list or, in a hiearchy of actors through a method known as costumes.

### Props
Props are static objects with no code embedded inside them. All props contain a ```drawObj()``` function which is called by the camera to draw the object to the screen. The camera passes data like the view matrix and perspective matrix, as well as shader programs and buffers to the ```drawObj()``` function of the prop that is currently being rendered. The ```drawObj()``` function is responsible for taking this data, and drawing the object to the screen. Unlike actors, props are static and have no code that is run, in order to do something they may be manually moved or changed by the mainloop, or by any actor they are attached to.

### Actors
Actors are similar to props with the key difference that they contain ```update()``` functions. Every frame an actor's ```update()``` function should be called. If the prop has costumes then those costumes will be updated as well if they are actor objects. Actors also contain a ```drawObj()``` function. This function does not draw the actor to the screen, instead it calls the ```drawObj()``` function of all the actor's costumes. If any of the costumes are props, then those will be drawn to the screen. If those costumes are actors their ```drawObj()``` function will be called which will go further down the costume hiearchy. Certain actors that aren't visible may not have any costumes (like the sfx3D object or the Camera objects.)

### Costumes
Costumes are a word given to actors or props that are a controlled by a higher actor. An example of this is the starship enemies, the starships are all code that calculates distance, movement, and positional data. AI starships also have Model props of starships that visualise them. These models are costumes, and they are controlled by and attached to an actor, another visual costume of the AIShip is a lazer effect. Costumes can also be actors for example the AIShip actor has a sfx3D costume for all of its engine noises. An actor may have zero or more costumes which can be actors or props. Actor costumes can also have costumes themselves. This results in game assets being stored in a hiearchy of top level Objects in ASSETS, which when their ```update()``` or ```drawObj()``` functions are called, it will call the same functions of any costumes, if the costume objects have costumes of their own, then those costumes will have their ```update()``` and ```drawObj()``` functions called as well. This cycle will repeat untill the lowest level cotumes have their functions called.

