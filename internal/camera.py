"""
10/26/2024
This file holds code for the rendering pipeline. All of this code is abstracted to a camera object to make drawing the scene easier.
"""

from OpenGL.GL import *
from ctypes import c_void_p
import pygame
import numpy
from pyglm import glm
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
        raise Exception(f"Shader \"{vertexshader}\" has error: {glGetShaderInfoLog(shader_vert)}")

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
        self.screensize = (1080, 720)
        self.perspectiveMatrix = glm.perspective(radians(fovy),self.screensize[0]/self.screensize[1],.001,1000)
        self.worldMatrix = glm.mat4(1)
        self.position = glm.vec4(0,0,0,1)
        self.direction = glm.vec4(0,0,1,0)
        self.up = glm.vec4(0,1,0,0)
        self.mx, self.my = 0, 0

        #Post processing effects
        self.__greyscale = 0

        self.screen = pygame.display.set_mode(self.screensize, pygame.OPENGL | pygame.DOUBLEBUF)

        # This is an error colour to show if something was not dran, this should ideally never be seen on the screen.
        glClearColor(1.0, 0.0, 1.0, 1)

        #Loads all of the shaders using the helper function.
        self.starshipShader = loadShaderProgram("shaders/starshipVertex.glsl","shaders/starshipFragment.glsl")
        self.skyboxShader = loadShaderProgram("shaders/skyboxVertex.glsl", "shaders/skyboxFragment.glsl")
        self.lazerShader = loadShaderProgram("shaders/lazerVertex.glsl", "shaders/lazerFragment.glsl")
        self.spriteShader = loadShaderProgram("shaders/screenSpaceSpriteVertex.glsl", "shaders/screenSpaceSpriteFragment.glsl")

        #A special shaderprogram that uses the screens image and manipulates it to post processing affect.
        self.postProcessingShader = loadShaderProgram("shaders/screenSpaceSpriteVertex.glsl","shaders/postProcessingFragment.glsl")

        #Creates a buffer to draw the scene to before post processing
        self.preProcessBuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER,self.preProcessBuffer)

        #Creates a depth buffer to allow correct drawing to preProcessTexture
        self.preProcessDepthBuffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER,self.preProcessDepthBuffer)
        glRenderbufferStorage(GL_RENDERBUFFER,GL_DEPTH_COMPONENT,self.screensize[0],self.screensize[1])
        glFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_RENDERBUFFER, self.preProcessDepthBuffer)

        #A texture to hold the image data of the pre processing pass
        self.preProcessTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,self.preProcessTexture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,self.screensize[0],self.screensize[1],0,GL_RGB,GL_UNSIGNED_BYTE,c_void_p(0))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glFramebufferTexture(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,self.preProcessTexture,0)

        self.frameBufferAttachments = (GL_COLOR_ATTACHMENT0)
        self.frameBufferAttachments = numpy.array(self.frameBufferAttachments, dtype=numpy.uint32)
        glDrawBuffers(1, self.frameBufferAttachments)

        self.vertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertexBuffer)

        self.indexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer)
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE):
            raise Exception("Post processing framebuffer failed to load.")

        glBindFramebuffer(GL_FRAMEBUFFER,0)
        glViewport(0, 0, self.screensize[0], self.screensize[1])
        # Enables some opengl functions (Blending (which allows semi transparent objects), and depth test (which tells opengl to draw closer objects over farther objects)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    def renderScene(self,scenemodeldata):
        #Rencers the scene to the pre processing buffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.preProcessBuffer)
        glViewport(0, 0, self.screensize[0], self.screensize[1])
        glBindBuffer(GL_ARRAY_BUFFER,self.vertexBuffer)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,self.indexBuffer)
        self.worldMatrix = glm.lookAt(glm.vec3(self.position), glm.vec3(self.position + self.direction),glm.vec3(self.up))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for object in scenemodeldata:
            object.drawObj(self.worldMatrix,self.perspectiveMatrix,
                           (self.starshipShader,self.skyboxShader,self.lazerShader,self.spriteShader),
                           self.vertexBuffer,
                           self.indexBuffer
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

        normalMatrix = glm.translate((0,0,-1))

        vertexdata = numpy.array(vertexdata, dtype=numpy.float32)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.preProcessTexture)

        glBufferData(GL_ARRAY_BUFFER, vertexdata.nbytes, vertexdata, GL_DYNAMIC_DRAW)

        # Tells the shaders where certain attributes are in the vertexdata list.
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), c_void_p(12))
        glEnableVertexAttribArray(1)
        glUniformMatrix4fv(glGetUniformLocation(self.postProcessingShader, "objectMatrix"), 1, GL_FALSE,
                           glm.value_ptr(normalMatrix))
        glUniform1i(glGetUniformLocation(self.postProcessingShader, "image"), 0)
        glUniform1f(glGetUniformLocation(self.postProcessingShader,"greyscale"),self.__greyscale)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, self.screensize[0], self.screensize[1])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draws the new image to the screen.
        glDrawArrays(GL_QUADS,0,4)
    def getScreenDimensions(self):
        return self.screensize

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
    def getPerspectiveMatrix(self):
        return self.perspectiveMatrix
    def getWorldMatrix(self):
        return self.worldMatrix

    def setPostProssGreyscale(self,value):
        if value > 1:
            value = 1
        elif value < 0:
            value = 0
        self.__greyscale = value

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
    def getAspectRatio(self):
        return self.screensize[0]/self.screensize[1]
