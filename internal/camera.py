"""
Skyler O'Bonsawin
1/10/2025
This file holds code for the rendering pipeline. All of this code is abstracted to a camera object to make drawing the scene easier.
"""

from OpenGL.GL import *
from ctypes import c_void_p
import pygame
import numpy
import glm
import random
from math import *

from internal.actors import Actor, StarShipTemplate
import internal.props as props
import internal.globalvariables as progvar


#A helper function used to load shaders (called by the camera)
def loadShaderProgram(vertexshader : str ,fragmentshader : str) -> int:
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
    shaderiv = 0
    if (not glGetShaderiv(shader_vert, GL_COMPILE_STATUS)):
        raise Exception(f"Shader \"{vertexshader}\" has error: {glGetShaderInfoLog(shader_vert)}")

    shader_frag = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(shader_frag, fragmentsrc)
    glCompileShader(shader_frag)
    shaderiv = 0
    if (not glGetShaderiv(shader_frag, GL_COMPILE_STATUS)):
        raise Exception(f"Shader \"{vertexshader}\" has error: {glGetShaderInfoLog(shader_frag)}")


    glAttachShader(shaderprogram, shader_vert)
    glAttachShader(shaderprogram, shader_frag)
    glLinkProgram(shaderprogram)
    if (not glGetProgramiv(shaderprogram, GL_LINK_STATUS)):
        raise Exception(f"Shaderprogram \"{vertexshader}\" and \"{fragmentshader}\" has error: {glGetProgramInfoLog(shaderprogram)}")

    return shaderprogram

#This is the basic camera class. It is used for debugging, and is a parent class for other camera types.
class Camera(Actor):
    def __init__(self, fovy : int, screenwh : tuple[int, int], rendertarget : int =0, costumes : tuple[props.Prop | Actor] =()):
        Actor.__init__(self,costumes)

        self.__screensize : tuple[int,int] = (screenwh[0], screenwh[1])
        self.perspectiveMatrix = glm.perspective(radians(fovy), self.__screensize[0] / self.__screensize[1], .001, 1000)
        self.worldMatrix = glm.mat4(1)
        self.position = glm.vec4(0,0,0,1)
        self.direction = glm.vec4(0,0,1,0)
        self.up = glm.vec4(0,1,0,0)
        self.mx, self.my = 0, 0

        #Post processing effects
        self.__greyscale = 0
        self.__shake = 0

        #This is the framebuffer the camera will render to. By default it is set to 0 (Directly to the pygame window) but it can be overridden to allow cameras to render to textures.
        self.__rendertarget = rendertarget

        # This is an error colour to show if something was not dran, this should ideally never be seen on the screen.
        glClearColor(1.0, 0.0, 1.0, 1)

        #Loads all of the shaders using the helper function.
        self.starshipShader = loadShaderProgram("shaders/modelVertex.glsl","shaders/modelFragment.glsl")
        self.skyboxShader = loadShaderProgram("shaders/skyboxVertex.glsl", "shaders/skyboxFragment.glsl")
        self.lazerShader = loadShaderProgram("shaders/lazerVertex.glsl", "shaders/lazerFragment.glsl")
        self.spriteShader = loadShaderProgram("shaders/screenSpaceSpriteVertex.glsl", "shaders/screenSpaceSpriteFragment.glsl")

        #A special shaderprogram that uses the screen's image and manipulates it to post processing affect.
        self.postProcessingShader = loadShaderProgram("shaders/postProcessingVertex.glsl","shaders/postProcessingFragment.glsl")

        #Creates a buffer to draw the scene to before post processing
        self.preProcessBuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER,self.preProcessBuffer)

        #Creates a depth buffer to allow correct drawing to preProcessTexture
        self.preProcessDepthBuffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER,self.preProcessDepthBuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self.__screensize[0], self.__screensize[1])
        glFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_RENDERBUFFER, self.preProcessDepthBuffer)

        #A texture to hold the image data of the pre processing pass
        self.preProcessTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.preProcessTexture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.__screensize[0], self.__screensize[1], 0, GL_RGB, GL_UNSIGNED_BYTE, c_void_p(0))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glFramebufferTexture(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,self.preProcessTexture,0)

        self.frameBufferAttachments = (GL_COLOR_ATTACHMENT0)
        self.frameBufferAttachments = numpy.array(self.frameBufferAttachments, dtype=numpy.uint32)
        glDrawBuffers(1, self.frameBufferAttachments)

        glBindFramebuffer(GL_FRAMEBUFFER,0)
        glViewport(0, 0, self.__screensize[0], self.__screensize[1])
        # Enables some opengl functions (Blending (which allows semi transparent objects), and depth test (which tells opengl to draw closer objects over farther objects)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def render(self) -> None:
        #Rencers the scene to the pre processing buffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.preProcessBuffer)
        glViewport(0, 0, self.__screensize[0], self.__screensize[1])
        self.worldMatrix = glm.lookAt(glm.vec3(self.position), glm.vec3(self.position + self.direction),glm.vec3(self.up))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for object in progvar.ASSETS:
            if object not in self.getCostumes():
                object.drawObj(self.worldMatrix,self.perspectiveMatrix,
                        (self.starshipShader,self.skyboxShader,self.lazerShader,self.spriteShader),
                        self
                        )

        #Takes the pre processing buffer, and puts it into the post processing shader.
        glUseProgram(self.postProcessingShader)
        glDepthFunc(GL_LESS)
        vertexdata = (
            -1.0, -1.0, 0.0, 0.0, 0.0,
            -1.0,  1.0, 0.0, 0.0, 1.0,
             1.0,  1.0, 0.0, 1.0, 1.0,
             1.0, -1.0, 0.0, 1.0, 0.0
        )

        screenTransform = glm.translate((random.random()*self.__shake,random.random()*self.__shake,random.random()*self.__shake))*glm.scale((1+self.__shake,1+self.__shake,1+self.__shake))

        vertexdata = numpy.array(vertexdata, dtype=numpy.float32)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.preProcessTexture)

        glBufferData(GL_ARRAY_BUFFER, vertexdata.nbytes, vertexdata, GL_DYNAMIC_DRAW)

        # Tells the shaders where certain attributes are in the vertexdata list.
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), c_void_p(12))
        glEnableVertexAttribArray(1)
        glUniformMatrix4fv(glGetUniformLocation(self.postProcessingShader, "screenTransform"), 1, GL_FALSE,
                           glm.value_ptr(screenTransform))
        glUniform1i(glGetUniformLocation(self.postProcessingShader, "image"), 0)
        glUniform1f(glGetUniformLocation(self.postProcessingShader,"greyscale"),self.__greyscale)

        glBindFramebuffer(GL_FRAMEBUFFER, self.__rendertarget)
        glViewport(0, 0, self.__screensize[0], self.__screensize[1])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draws the new image to the screen.
        glDrawArrays(GL_QUADS,0,4)

    def getScreenDimensions(self) -> tuple[int,int]:
        return self.__screensize

    #Renderes to the camera's view object when called.
    def update(self) -> None:
        self.render()

    def getPerspectiveMatrix(self) -> glm.mat4:
        return self.perspectiveMatrix
    def getWorldMatrix(self) -> glm.mat4:
        return self.worldMatrix

    def setPostProssGreyscale(self,value : float) -> None:
        if value > 1:
            value = 1
        elif value < 0:
            value = 0
        self.__greyscale = value

    def setPostProssShake(self,value : float) -> None:
        if value > 1:
            value = 1
        elif value < 0:
            value = 0
        self.__shake = value
    def getAspectRatio(self) -> float:
        return self.getScreenDimensions()[0]/self.getScreenDimensions()[1]

class ShipCamera(Camera):
    def __init__(self,fovy : int,screenwh : tuple[int,int],rendertarget : int =0,parentship : StarShipTemplate | None =None,offset : glm.mat4 = glm.mat4(1)):
        Camera.__init__(self,fovy,screenwh,rendertarget)
        self.__parentship = parentship
        self.__offset = offset

    def update(self) -> None:
        self.render()
        if self.__parentship != None:
            self.position = (self.__parentship.getPos() * (self.__parentship.getRot()))*self.__offset*glm.vec4(0,0,0,1)
            self.direction = self.__parentship.getRot() * self.__offset * glm.vec4(0, 0, 1, 0)
            self.up = self.__parentship.getRot() * self.__offset * glm.vec4(0, 1, 0, 0)

    def attachToShip(self,target : StarShipTemplate) -> None:
        self.__parentship = target

    def getShip(self) -> StarShipTemplate:
        return self.__parentship
