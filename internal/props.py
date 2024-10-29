"""
10/26/2024
This file holds code for props that can be drawn to a scene. Props are static objects with no behavior.
They can move and rotate, but have no way of doing this on their own and it can only be done through a external function.
Props would make up static parts of the game, like the level geomery, or a tree, something to show, but with no behavior.
"""

from OpenGL.GL import *
from ctypes import c_void_p
import pygame
import numpy
import glm

class Model:
    def __init__(self, ObjFilePath, ColourMapPath, GlowMapPath, ID, shaderID = 0, directXTexture = True):
        self.__translation = glm.mat4(1)
        self.__rotation = glm.mat4(1)
        self.__scale = glm.mat4(1)

        self.mousebuttondownlastframe = False
        self.__shaderID = shaderID
        self.__ID = ID
        objData = []
        with open(ObjFilePath, 'r') as objFile:
            objData = objFile.readlines()

        vertpos = []
        normpos = []
        texpos = []

        vertexdata = []
        maxindex = 0
        indexdata = []
        alreadymadevertdata = []

        #Reads all of the verticies, normals, faces, and texture coords in the .obj file and then stores them in the vertex and index data lists.
        for databit in objData:

            #Stores sets of texture coords into a temporary array.
            if databit.startswith("vt"):
                databitlist = databit.split(' ')[1:]
                databitlistconverted = []
                for value in databitlist:
                    databitlistconverted.append(float(value))
                texpos.append(databitlistconverted)
                print(databitlistconverted)

            #Stores a list of normals into a temporary array.
            elif databit.startswith('vn'):
                databitlist = databit.split(' ')[1:]
                databitlistconverted = []
                for value in databitlist:
                    databitlistconverted.append(float(value))
                normpos.append(databitlistconverted)

            #Stors a list of coordinates into a temporary array.
            elif databit.startswith("v"):
                databitlist = databit.split(' ')[1:]
                databitlistconverted = []
                for value in databitlist:
                    databitlistconverted.append(float(value))
                vertpos.append(databitlistconverted)

            #This part takes the temporary list of the three vertex, normal, and tex coord lists, from the previous three loops and then puts them into a vertex array
            elif databit.startswith('f'):
                databitlist = databit.split()[1:]
                for face in databitlist:
                    if face.strip() not in alreadymadevertdata:
                        alreadymadevertdata.append(face.strip())


                        indexes = face.split('/')
                        for vert in vertpos[int(indexes[0]) - 1]:
                            vertexdata.append(vert)
                        try:
                            for norm in normpos[int(indexes[2]) - 1]:
                                vertexdata.append(norm)
                        #If the normal value is blank, it will fill the spaces with blank values
                        except:
                            vertexdata.append(0.0)
                            vertexdata.append(0.0)
                            vertexdata.append(0.0)
                            print(f"Normal for face {databitlist} was not found.")
                        try:
                            print(texpos[int(4) - 1])
                            for tex in texpos[int(indexes[1]) - 1]:
                                vertexdata.append(tex)
                                print(tex)
                        except:
                            vertexdata.append(0.0)
                            vertexdata.append(0.0)
                            print(f"Tex coord data for face {databitlist} was not found.")
                        indexdata.append(maxindex)
                        maxindex += 1
                    else:
                        indexdata.append(alreadymadevertdata.index(face))

        #Converts the vertex and index arrays to a usable format.
        self.__vertexdata = numpy.array(vertexdata,dtype=numpy.float32)
        self.__indexdata = numpy.array(indexdata,dtype=numpy.uint32)

        #Generates the texture.
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        textureData = pygame.image.load(ColourMapPath).convert_alpha()
        textureData = pygame.transform.flip(textureData,False,directXTexture)
        image_width, image_height = textureData.get_rect().size
        image = pygame.image.tobytes(textureData,"RGBA")
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,image)
        glGenerateMipmap(GL_TEXTURE_2D)

        self.glow = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.glow)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        textureData = pygame.image.load(GlowMapPath).convert_alpha()
        textureData = pygame.transform.flip(textureData, False, directXTexture)
        image_width, image_height = textureData.get_rect().size
        image = pygame.image.tobytes(textureData, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glGenerateMipmap(GL_TEXTURE_2D)

    def getID(self):
        return self.__ID
    def getIsActor(self):
        return False

    def translate(self,translation):
        self.__translation *= translation
    def setpos(self,position):
        self.__translation = position
    def getPos(self):
        return self.__translation;

    def rotate(self,angle):
        self.__translation *= angle
    def setrot(self,rotation):
        self.__translation = rotation
    def getRot(self):
        return self.__rotation;

    def resize(self,resize):
        self.__scale *= resize
    def setScale(self,size):
        self.__scale = size
    def getScale(self):
        return self.__scale

    def getMatrix(self):
        return self.translation * self.rotation * self.scale


    def drawObj(self,worldMatrix,perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist
                ):
        self.bindTexture()
        objMatrix = self.translation * self.rotation * self.scale

        glDepthFunc(GL_LESS)
        glUseProgram(shaderlist[0])
        glBindBuffer(GL_ARRAY_BUFFER, shaderlist[0])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexbufferlist[0])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.__indexdata.nbytes, self.__indexdata, GL_STATIC_DRAW)
        glBufferData(GL_ARRAY_BUFFER, self.__vertexdata.nbytes, self.__vertexdata, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(GLfloat), c_void_p(24))
        glEnableVertexAttribArray(2)
        glUniformMatrix4fv(glGetUniformLocation(shaderlist[0], "objMatrix"), 1, GL_FALSE,
                           glm.value_ptr(objMatrix))
        glUniformMatrix4fv(glGetUniformLocation(shaderlist[0], "perspectiveMatrix"), 1, GL_FALSE,
                           glm.value_ptr(perspectiveMatrix))
        glUniformMatrix4fv(glGetUniformLocation(shaderlist[0], "worldMatrix"), 1, GL_FALSE,
                           glm.value_ptr(worldMatrix))
        glUniform3f(glGetUniformLocation(shaderlist[0], "lightPos"), 1, 0, 0)
        glUniform1i(glGetUniformLocation(shaderlist[0], 'colourMap'), 0)
        glUniform1i(glGetUniformLocation(shaderlist[0], "glowMap"), 1)

        glDrawElements(GL_TRIANGLES, len(self.__indexdata), GL_UNSIGNED_INT, None)

    #A function to call to prepare the texture to be drawn.
    def bindTexture(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.glow)

    def getVertexData(self):
        return self.__vertexdata
    def getIndexData(self):
        return self.__indexdata
    def getShader(self):
        return self.__shaderID
    def getCostumeData(self):
        return [self]

class Skybox:
    def __init__(self, texturepath,ID):
        self.__ID = ID
        vertexdata = (
             1.0, 1.0, -1.0,
             1.0,-1.0, -1.0,
             1.0, 1.0, 1.0,
             1.0,-1.0, 1.0,
            -1.0, 1.0,-1.0,
            -1.0,-1.0,-1.0,
            -1.0, 1.0, 1.0,
            -1.0,-1.0, 1.0

        )

        indexdata = (
            4,2,0,
            2,7,3,
            6,5,7,
            1,7,5,
            0,3,1,
            4,1,5,
            4,6,2,
            2,6,7,
            6,4,5,
            1,3,7,
            0,2,3,
            4,0,1
        )

        self.__vertexdata = numpy.array(vertexdata, dtype=numpy.float32)
        self.__indexdata = numpy.array(indexdata, dtype=numpy.uint32)

        cubeimagefilepaths = (
            f"{texturepath}/right.png",
            f"{texturepath}/left.png",
            f"{texturepath}/top.png",
            f"{texturepath}/bottom.png",
            f"{texturepath}/front.png",
            f"{texturepath}/back.png"
        )

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        for i in range(len(cubeimagefilepaths)):
            file = pygame.image.load(cubeimagefilepaths[i])
            filedata = pygame.image.tostring(file,"RGBA")

            image_width, image_height = file.get_rect().size

            if not(filedata):
                raise Exception(f"File {cubeimagefilepaths[i]} failed to load")

            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                0,
                GL_RGBA,
                image_width,
                image_height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                filedata
            )
    def getID(self):
        return self.__ID

    def drawObj(self, worldMatrix, perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist
                ):
        self.bindTexture()

        glDepthFunc(GL_EQUAL)
        glUseProgram(shaderlist[1])
        glBindBuffer(GL_ARRAY_BUFFER, vertexbufferlist[1])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexbufferlist[1])

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), c_void_p(0))
        glEnableVertexAttribArray(0)

        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.__indexdata.nbytes, self.__indexdata, GL_STATIC_DRAW)
        glBufferData(GL_ARRAY_BUFFER, self.__vertexdata.nbytes, self.__vertexdata, GL_STATIC_DRAW)

        glUniformMatrix4fv(glGetUniformLocation(shaderlist[1], "worldMatrix"), 1, GL_FALSE,
                           glm.value_ptr(worldMatrix))
        glUniformMatrix4fv(glGetUniformLocation(shaderlist[1], "perspectiveMatrix"), 1, GL_FALSE,
                           glm.value_ptr(perspectiveMatrix))
        glUniform1i(glGetUniformLocation(shaderlist[1], 'skyboxTexture'), 0)

        glDrawElements(GL_TRIANGLES, len(self.__indexdata), GL_UNSIGNED_INT, None)

    def getIsActor(self):
        return False
    def bindTexture(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
    def getVertexData(self):
        return self.__vertexdata
    def getIndexData(self):
        return self.__indexdata
    def getShader(self):
        return 1
    def getCostumeData(self):
        return [self]