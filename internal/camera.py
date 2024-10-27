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
        self.perspectiveMatrix = glm.perspective(radians(fovy),self.screensize[0]/self.screensize[1],.001,100)
        self.position = glm.vec4(0,0,0,1)
        self.direction = glm.vec4(0,0,1,0)
        self.up = glm.vec4(0,1,0,0)
        self.mx, self.my = 0, 0

        self.screen = pygame.display.set_mode(self.screensize, pygame.OPENGL | pygame.DOUBLEBUF)

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

        print(glGetShaderiv(shader_vert,GL_COMPILE_STATUS))

        shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(shader_frag, fragmentsrc)
        glCompileShader(shader_frag)

        print(glGetShaderiv(shader_vert, GL_COMPILE_STATUS))

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

        print(glGetShaderiv(shader_vert, GL_COMPILE_STATUS))

        shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(shader_frag, fragmentsrc)
        glCompileShader(shader_frag)

        print(glGetShaderiv(shader_vert, GL_COMPILE_STATUS))

        glAttachShader(self.skyboxShader, shader_vert)
        glAttachShader(self.skyboxShader, shader_frag)
        glLinkProgram(self.skyboxShader)

        self.skyboxVertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.skyboxVertexBuffer)

        self.skyboxIndexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.skyboxIndexBuffer)

    def renderScene(self,scenemodeldata):
        for model in scenemodeldata:
            self.drawObj(model)

    #Draws a given object to the screen. (NOTE: this function takes multiple different classes as input)
    def drawObj(self,object):
        worldMatrix = glm.lookAt(glm.vec3(self.position),glm.vec3(self.position+self.direction),glm.vec3(self.up))
        vertexdata = object.getVertexData()
        indexdata = object.getIndexData()
        if object.getShader() == 0:
            object.bindTexture()

            glDepthFunc(GL_LESS)
            glUseProgram(self.starshipShader)
            glBindBuffer(GL_ARRAY_BUFFER,self.starshipVertexBuffer)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.starshipIndexBuffer)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indexdata.nbytes, indexdata, GL_STATIC_DRAW)
            glBufferData(GL_ARRAY_BUFFER, vertexdata.nbytes, vertexdata, GL_STATIC_DRAW)

            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), c_void_p(0))
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), c_void_p(12))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), c_void_p(24))
            glEnableVertexAttribArray(2)

            glUniformMatrix4fv(glGetUniformLocation(self.starshipShader, "objMatrix"), 1, GL_FALSE, glm.value_ptr(object.objMatrix))
            glUniformMatrix4fv(glGetUniformLocation(self.starshipShader, "perspectiveMatrix"), 1, GL_FALSE, glm.value_ptr(self.perspectiveMatrix))
            glUniformMatrix4fv(glGetUniformLocation(self.starshipShader, "worldMatrix"), 1, GL_FALSE, glm.value_ptr(worldMatrix))
            glUniform3f(glGetUniformLocation(self.starshipShader, "lightPos"), 1, 0, 0)
            glUniform1i(glGetUniformLocation(self.starshipShader, 'colourMap'), 0)

        elif object.getShader() == 1:
            object.bindTexture()

            glDepthFunc(GL_EQUAL)
            glUseProgram(self.skyboxShader)
            glBindBuffer(GL_ARRAY_BUFFER,self.skyboxVertexBuffer)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.skyboxIndexBuffer)

            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), c_void_p(0))
            glEnableVertexAttribArray(0)

            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indexdata.nbytes, indexdata, GL_STATIC_DRAW)
            glBufferData(GL_ARRAY_BUFFER, vertexdata.nbytes, vertexdata, GL_STATIC_DRAW)


            glUniformMatrix4fv(glGetUniformLocation(self.skyboxShader,"worldMatrix"),1,GL_FALSE,glm.value_ptr(worldMatrix))
            glUniformMatrix4fv(glGetUniformLocation(self.skyboxShader,"perspectiveMatrix"),1,GL_FALSE,glm.value_ptr(self.perspectiveMatrix))
            glUniform1i(glGetUniformLocation(self.starshipShader, 'skyboxTexture'), 0)


        glDrawElements(GL_TRIANGLES, len(indexdata), GL_UNSIGNED_INT, None)

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