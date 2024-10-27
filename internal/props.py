"""
10/26/2024
This file holds code for props that can be drawn to a scene. Props are static objects with no behavior.
They can move and rotate, but have no way of doing this on their own and it can only be done through a external function.
Props would make up static parts of the game, like the level geomery, or a tree, something to show, but with no behavior.
"""

from OpenGL.GL import *
import pygame
import numpy
import glm

#The problematic code is somewhere in this function.
class Model:
    def __init__(self, ObjFilePath, ColourMapPath, GlowMapPath, ID, shaderID = 0, directXTexture = True):
        self.objMatrix = glm.mat4(1)
        self.mousebuttondownlastframe = False
        self.__shaderID = shaderID
        self.ID = ID
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
        return self

class Skybox:
    def __init__(self, texturepath,ID):
        self.ID = ID
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
        return self