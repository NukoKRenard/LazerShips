"""
10/26/2024
This file holds code for the rendering pipeline. All of this code is abstracted to a camera object to make drawing the scene easier.
"""

from OpenGL.GL import *
from ctypes import c_void_p
import pygame
import glm
from math import *

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

        # Opens, reads, and stores the uncompiled vertex shader in a string.
        vertexsrc = ""
        with open("shaders/starshipVertex.glsl", 'r') as vertexshaderfile:
            vertexsrc = vertexshaderfile.read()
        # Opens, reads, and stores the uncompiled fragment shader in a string.
        fragmentsrc = ""
        with open("shaders/starshipFragment.glsl", 'r') as fragmentshaderfile:
            fragmentsrc = fragmentshaderfile.read()

        self.starshipShader = glCreateProgram()

        shader_vert = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(shader_vert, vertexsrc)
        glCompileShader(shader_vert)

        shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(shader_frag, fragmentsrc)
        glCompileShader(shader_frag)

        glAttachShader(self.starshipShader, shader_vert)
        glAttachShader(self.starshipShader, shader_frag)
        glLinkProgram(self.starshipShader)

        self.starshipVertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.starshipVertexBuffer)

        self.starshipIndexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.starshipIndexBuffer)

        glEnable(GL_DEPTH_TEST)

        # Opens, reads, and stores the uncompiled vertex shader in a string.
        vertexsrc = ""
        with open("shaders/skyboxVertex.glsl", 'r') as vertexshaderfile:
            vertexsrc = vertexshaderfile.read()
        # Opens, reads, and stores the uncompiled fragment shader in a string.
        fragmentsrc = ""
        with open("shaders/skyboxFragment.glsl", 'r') as fragmentshaderfile:
            fragmentsrc = fragmentshaderfile.read()

        self.skyboxShader = glCreateProgram()

        shader_vert = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(shader_vert, vertexsrc)
        glCompileShader(shader_vert)

        shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(shader_frag, fragmentsrc)
        glCompileShader(shader_frag)

        glAttachShader(self.skyboxShader, shader_vert)
        glAttachShader(self.skyboxShader, shader_frag)
        glLinkProgram(self.skyboxShader)

        self.skyboxVertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.skyboxVertexBuffer)

        self.skyboxIndexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.skyboxIndexBuffer)

        vertexsrc = ""
        with open("shaders/lazerVertex.glsl", 'r') as vertexshaderfile:
            vertexsrc = vertexshaderfile.read()
        # Opens, reads, and stores the uncompiled fragment shader in a string.
        fragmentsrc = ""
        with open("shaders/lazerFragment.glsl", 'r') as fragmentshaderfile:
            fragmentsrc = fragmentshaderfile.read()

        self.lazerShader = glCreateProgram()

        shader_vert = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(shader_vert, vertexsrc)
        glCompileShader(shader_vert)

        shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(shader_frag, fragmentsrc)
        glCompileShader(shader_frag)

        glAttachShader(self.lazerShader, shader_vert)
        glAttachShader(self.lazerShader, shader_frag)
        glLinkProgram(self.lazerShader)

        self.lazerVertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.lazerVertexBuffer)

        self.lazerIndexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.lazerIndexBuffer)

    def renderScene(self,scenemodeldata):
        worldMatrix = glm.lookAt(glm.vec3(self.position), glm.vec3(self.position + self.direction), glm.vec3(self.up))
        for object in scenemodeldata:
            object.drawObj(worldMatrix,self.perspectiveMatrix,
                           (self.starshipShader,self.skyboxShader,self.lazerShader),
                           (self.starshipVertexBuffer,self.skyboxVertexBuffer,self.lazerVertexBuffer),
                           (self.starshipIndexBuffer,self.skyboxIndexBuffer,self.lazerIndexBuffer)
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
        self.parentship = parentship

    def updateCamera(self,deltaTime):
        self.position = self.parentship.getPos()*(self.parentship.getRot()*glm.vec4(0,10,-20,1))
        self.direction = self.parentship.getRot()*glm.vec4(0,0,1,0)
        self.up = self.parentship.getRot()*glm.vec4(0,1,0,0)

    def attachToShip(self,target):
        self.parentship = target