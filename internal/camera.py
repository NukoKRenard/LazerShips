"""
10/26/2024
This file holds code for the rendering pipeline. All of this code is abstracted to a camera object to make drawing the scene easier.
"""

from OpenGL.GL import *
from ctypes import c_void_p
import pygame
import glm
from math import *

#A helper function used to load shaders (called by the camera)
def loadShaderProgram(vertexshader,fragmentshader):
    # Opens, reads, and stores the uncompiled vertex shader in a string.
    vertexsrc = ""
    with open(vertexshader, 'r') as vertexshaderfile:
        vertexsrc = vertexshaderfile.read()
    # Opens, reads, and stores the uncompiled fragment shader in a string.
    fragmentsrc = ""
    with open(fragmentshader, 'r') as fragmentshaderfile:
        fragmentsrc = fragmentshaderfile.read()

    shaderprogram = glCreateProgram()

    shader_vert = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(shader_vert, vertexsrc)
    glCompileShader(shader_vert)
    shaderiv = 0;
    if (not glGetShaderiv(shader_vert, GL_COMPILE_STATUS)):
        raise Exception(f"Shader \"{vertexshader}\" has error: {glGetShaderInfoLog(shader_frag)}")

    shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(shader_frag, fragmentsrc)
    glCompileShader(shader_frag)
    shaderiv = 0;
    if (not glGetShaderiv(shader_frag, GL_COMPILE_STATUS)):
        raise Exception(f"Shader \"{vertexshader}\" has error: {glGetShaderInfoLog(shader_frag)}")


    glAttachShader(shaderprogram, shader_vert)
    glAttachShader(shaderprogram, shader_frag)
    glLinkProgram(shaderprogram)
    if (not glGetProgramiv(shaderprogram, GL_LINK_STATUS)):
        raise Exception(f"Shaderprogram \"{vertexshader}\" and \"{fragmentshader}\" has error: {glGetProgramInfoLog(shaderprogram)}")

    return shaderprogram

#This is the basic camera class. It is used for debugging, and is a parent class for other camera types.
class Camera:
    def __init__(self,fovy):
        self.screensize = (1920, 1080)
        self.perspectiveMatrix = glm.perspective(radians(fovy),self.screensize[0]/self.screensize[1],.001,1000)
        self.position = glm.vec4(0,0,0,1)
        self.direction = glm.vec4(0,0,1,0)
        self.up = glm.vec4(0,1,0,0)
        self.mx, self.my = 0, 0

        self.screen = pygame.display.set_mode(self.screensize, pygame.OPENGL | pygame.DOUBLEBUF)

        # This is an error colour to show if something was not dran, this should ideally never be seen on the screen.

        glClearColor(1.0, 0.0, 1.0, 1)


        self.starshipShader = loadShaderProgram("shaders/starshipVertex.glsl","shaders/starshipFragment.glsl")
        self.skyboxShader = loadShaderProgram("shaders/skyboxVertex.glsl", "shaders/skyboxFragment.glsl")
        self.lazerShader = loadShaderProgram("shaders/lazerVertex.glsl", "shaders/lazerFragment.glsl")
        self.spriteShader = loadShaderProgram("shaders/screenSpaceSpriteVertex.glsl", "shaders/screenSpaceSpriteFragment.glsl")


        self.vertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffer)

        self.indexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def renderScene(self,scenemodeldata):
        glBindBuffer(GL_ARRAY_BUFFER,self.vertexBuffer)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.indexBuffer)
        worldMatrix = glm.lookAt(glm.vec3(self.position), glm.vec3(self.position + self.direction), glm.vec3(self.up))
        for object in scenemodeldata:
            object.drawObj(worldMatrix,self.perspectiveMatrix,
                           (self.starshipShader,self.skyboxShader,self.lazerShader,self.spriteShader),
                           self.vertexBuffer,
                           self.indexBuffer
                           )

    #Calculates camera movement, Very crude as of right now
    def updateCamera(self,deltaTime):
        if pygame.mouse.get_pos() != (0,0) and pygame.mouse.get_pos() != (self.screensize[0]//2,self.screensize[1]//2):
            mx, my = ((pygame.mouse.get_pos()[0] / self.screensize[0]) - .5)*2, ((pygame.mouse.get_pos()[1] / self.screensize[1]) - .5)*2
            self.mx += mx
            self.my += my
            pygame.mouse.set_pos((self.screensize[0]//2,self.screensize[1]//2))
            self.direction = glm.vec4(0,0,1,0)*glm.rotate(self.my/10,(-1,0,0))
            self.direction *= glm.rotate(self.mx/10,(0,1,0))

        if pygame.key.get_pressed()[pygame.K_w]:
            self.position.z += 1/30*deltaTime
        if pygame.key.get_pressed()[pygame.K_s]:
            self.position.z -= 1/30*deltaTime
        if pygame.key.get_pressed()[pygame.K_a]:
            self.position.x += 1/30*deltaTime
        if pygame.key.get_pressed()[pygame.K_d]:
            self.position.x -= 1/30*deltaTime
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            self.position.y += 1/30*deltaTime
        if pygame.key.get_pressed()[pygame.K_LCTRL]:
            self.position.y -= 1 / 30 * deltaTime

class ShipCamera(Camera):
    def __init__(self,fovy,parentship=None):
        Camera.__init__(self,fovy)
        self.__parentship = parentship

    def updateCamera(self):
        if self.__parentship != None:
            self.position = self.__parentship.getPos() * (self.__parentship.getRot() * (glm.vec4(0, 10, -20, 1)-glm.vec4(self.__parentship.getVelocity()*5,0)))
            self.direction = self.__parentship.getRot() * glm.vec4(0, 0, 1, 0)
            self.up = self.__parentship.getRot() * glm.vec4(0, 1, 0, 0)

    def attachToShip(self,target):
        self.__parentship = target

    def getShip(self):
        return self.__parentship