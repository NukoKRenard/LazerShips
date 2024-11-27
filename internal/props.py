"""
10/26/2024
This file holds code for props that can be drawn to a scene. Props are static objects with no behavior.
They can move and rotate, but have no way of doing this on their own and it can only be done through a external function.
Props would make up static parts of the game, like the level geomery, or a tree, something to show, but with no behavior.
"""
import internal.globalvariables as progvar
from OpenGL.GL import *
from ctypes import c_void_p
import pygame
import numpy
import glm

#Parent class used to define global functions.
class Object:
    def removefromgame(self):
        try:
            progvar.ASSETS.remove(self)
        except:
            print(f"{self} not in assets list.")

#This is a basic model, everything you see on screen are props or costumes (costumes are props connected to actors.)
class Model(Object):
    def __init__(self, ObjFilePath, ColourMapPath, GlowMapPath, ID, shaderID = 0, directXTexture = True):
        #Props move using matrix math.
        self.__translation = glm.mat4(1)
        self.__rotation = glm.mat4(1)
        self.__scale = glm.mat4(1)

        self.__shaderID = shaderID
        self.__ID = ID
        objData = []

        #Opens the file and read it
        with open(ObjFilePath, 'r') as objFile:
            objData = objFile.readlines()

        #The following code is to parse the file into a program useable format.
        #Temporary lists that hold different vertex attributes. These will be moved into the vertexdata list when the indexdata is read.
        vertpos = []
        normpos = []
        texpos = []

        vertexdata = []
        maxindex = 0
        indexdata = []
        #This list holds any indecies that have already been made. It is used so that we don't have to load new vertexes, and can just reuse old ones.
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
                    #This if statement tests if we already have added that vertex into the vertexdata list (Some polygons shader vertexes with others, by using less vertexes our program becomes more efficient.)
                    if face.strip() not in alreadymadevertdata:
                        alreadymadevertdata.append(face.strip())

                        #Splits the index data into its positional, texture, and normal data.
                        indexes = face.split('/')
                        #Adds all of the found vertecies into the temporary vertexdata variable.
                        for vert in vertpos[int(indexes[0]) - 1]:
                            vertexdata.append(vert)
                        #Adds all of the found normal data into the temporary normaldata variable. If the normals are not found it will append an empty value to avoid crashes.
                        try:
                            for norm in normpos[int(indexes[2]) - 1]:
                                vertexdata.append(norm)
                        #If the normal value is blank, it will fill the spaces with blank values
                        except:
                            vertexdata.append(0.0)
                            vertexdata.append(0.0)
                            vertexdata.append(0.0)
                            print(f"Normal for face {databitlist} was not found.")
                        #Adds all of the found texture data into the temporary texturedata variable. If the textures are not found it will append an empty value to avoid crashes.
                        try:
                            for tex in texpos[int(indexes[1]) - 1]:
                                vertexdata.append(tex)
                        except:
                            vertexdata.append(0.0)
                            vertexdata.append(0.0)
                            print(f"Tex coord data for face {databitlist} was not found.")
                        #Adds the new index to the indexdata list.
                        indexdata.append(maxindex)
                        #Increments the index number so that the next index is 1 higher.
                        maxindex += 1
                    else:
                        #If the face already exists, it locates its index value and adds it to the indexdata list.
                        indexdata.append(alreadymadevertdata.index(face))

        #Converts the vertex and index arrays to a format useable by OpenGL.
        self.__vertexdata = numpy.array(vertexdata,dtype=numpy.float32)
        self.__indexdata = numpy.array(indexdata,dtype=numpy.uint32)

        #Generates the texture.
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        #These are settings that must be set for OpenGL
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        #Loads the image and puts it in the texture.
        textureData = pygame.image.load(ColourMapPath)
        textureData = pygame.transform.flip(textureData,False,directXTexture)
        image_width, image_height = textureData.get_rect().size
        image = pygame.image.tobytes(textureData,"RGBA")
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,image)
        glGenerateMipmap(GL_TEXTURE_2D)

        #Loads the glow and roughness map and puts them in a seperate texture (These colours are not directly shown to the player, but are used in fragment shader calculations.)
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

    #Get the props ID
    def getID(self):
        return self.__ID
    #Only actors have update function. This method stops crashes by not allowing non actors to be updated.
    def getIsActor(self):
        return False

    #Movement functions
    def translate(self,translation):
        self.__translation *= translation
    def setpos(self,position):
        self.__translation = position
    def getPos(self):
        return self.__translation;

    #Rotation functions
    def rotate(self,angle):
        self.__rotation *= angle
    def setrot(self,rotation):
        self.__rotation = rotation
    def getRot(self):
        return self.__rotation

    #Scaling functions
    def resize(self,resize):
        self.__scale *= resize
    def setScale(self,size):
        self.__scale = size
    def getScale(self):
        return self.__scale

    #Gets the value of the position, rotation, and scale rotation multiplied together.
    def getMatrix(self):
        return self.translation * self.rotation * self.scale

    #Draws the object to the screen. This similar to the pygame sprite's draw function.
    def drawObj(self,worldMatrix,perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist,
                parentMatrix=glm.vec4(1)
                ):

        #Binds the texture to the buffer to be sent to the shader.
        self.bindTexture()
        #Binds the skybox texture (This is used to calculate reflections.)
        progvar.SKYBOX.bindTexture(GL_TEXTURE2)
        objMatrix = parentMatrix*(self.__translation * self.__rotation * self.__scale)

        #Binds the shaderprogram and buffers. (Tells OpenGL that these are the shaders/buffers that we want to use to draw the ship)
        glDepthFunc(GL_LESS)
        glUseProgram(shaderlist[0])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.__indexdata.nbytes, self.__indexdata, GL_STATIC_DRAW)
        glBufferData(GL_ARRAY_BUFFER, self.__vertexdata.nbytes, self.__vertexdata, GL_STATIC_DRAW)

        #Tells the shaders where certain attributes are in the vertexdata list.
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
        glUniform1i(glGetUniformLocation(shaderlist[0], "reflection"), 2)

        #Draws the prop to the screen.
        glDrawElements(GL_TRIANGLES, len(self.__indexdata), GL_UNSIGNED_INT, None)

    #A function to call to prepare the texture to be drawn.
    def bindTexture(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.glow)

#This is the skybox class that shows the space scene the ships all fight in.
class Skybox(Object):
    def __init__(self, texturepath,ID):
        self.__ID = ID

        #Vertex data for a cube. This is what the skybox is put on.
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

        #Index data for the cube. This tells the shader how to use the vertex data.
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

        #Converts the vertex and index data into a format useable by OpenGL
        self.__vertexdata = numpy.array(vertexdata, dtype=numpy.float32)
        self.__indexdata = numpy.array(indexdata, dtype=numpy.uint32)

        #The path to all of the textures for the cubemep of the skybox
        cubeimagefilepaths = (
            f"{texturepath}/right.png",
            f"{texturepath}/left.png",
            f"{texturepath}/top.png",
            f"{texturepath}/bottom.png",
            f"{texturepath}/front.png",
            f"{texturepath}/back.png"
        )

        #Generates a cubemap texture
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        #Adds every face to the cubemap.
        for i in range(len(cubeimagefilepaths)):
            file = pygame.image.load(cubeimagefilepaths[i])
            filedata = pygame.image.tostring(file,"RGBA")

            image_width, image_height = file.get_rect().size

            if not(filedata):
                raise Exception(f"File {cubeimagefilepaths[i]} failed to load")

            #Loads the texture into the cubemap.
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,filedata)

    #Get function for the ID of the prop.
    def getID(self):
        return self.__ID

    #Draws the object to the screen.
    def drawObj(self, worldMatrix, perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist
                ):

        #Binds the textures to prepare to be drawn to the screen.
        self.bindTexture()

        #Binds the shaderprogram and buffers. (Tells OpenGL that these are the shaders/buffers that we want to use to draw the skybox)
        glDepthFunc(GL_EQUAL)
        glUseProgram(shaderlist[1])

        #Tells the shader where the vertecies of the skybox are located.
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), c_void_p(0))
        glEnableVertexAttribArray(0)

        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.__indexdata.nbytes, self.__indexdata, GL_STATIC_DRAW)
        glBufferData(GL_ARRAY_BUFFER, self.__vertexdata.nbytes, self.__vertexdata, GL_STATIC_DRAW)

        glUniformMatrix4fv(glGetUniformLocation(shaderlist[1], "worldMatrix"), 1, GL_FALSE,
                           glm.value_ptr(worldMatrix))
        glUniformMatrix4fv(glGetUniformLocation(shaderlist[1], "perspectiveMatrix"), 1, GL_FALSE,
                           glm.value_ptr(perspectiveMatrix))
        glUniform1i(glGetUniformLocation(shaderlist[1], 'skyboxTexture'), 0)

        #Draws the skybox to the screen.
        glDrawElements(GL_TRIANGLES, len(self.__indexdata), GL_UNSIGNED_INT, None)

    def getIsActor(self):
        return False

    #Bind the skyboxes textures to the buffers to prepare them for drawing. The skybox texture can also be used in reflections, which is why there is an option to bind it to a different buffer.
    def bindTexture(self,buffer=GL_TEXTURE0):
        glActiveTexture(buffer)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

#A special effects props that visualises attacks of different ships.
class Lazer(Object):
    def __init__(self, startpos, endpos, color):
        #Weither the lazer will be drawn to the screen or not
        self.__isvisible = False

        #The start and end pos of the lazer.
        self.__start = glm.vec4(startpos,1)
        self.__end = glm.vec4(endpos,1)

        #The colour of the lazer
        self.__color = glm.vec3(color)
    #Draws the lazer to the screen.
    def drawObj(self, worldMatrix, perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist,
                parentMatrix=glm.vec4(1)
                ):

        if self.__isvisible:
            #Gets the camera position.
            campos = glm.inverse(worldMatrix)*glm.vec4(0,0,0,1)
            #The camera position can not equal zero or all of the lazers dissapear. If it does equal zero it increments it slightly so the lazers still show.
            if campos == glm.vec4(0,0,0,1):
                campos = glm.vec4(0,0,0.1,1)
            #How offset the corner of the plane should be from the start and end pos.
            corneroffset = glm.normalize(glm.cross(self.__end.xyz-self.__start.xyz,campos.xyz))
            # modifies the width of the lazer
            corneroffset *= .2
            #Generates all of the corners of the 2D plane, and loads them into a promise.
            vertexdata = (
                self.__start.x+corneroffset.x, self.__start.y+corneroffset.y, self.__start.z+corneroffset.z,
                self.__start.x-corneroffset.x, self.__start.y-corneroffset.y, self.__start.z-corneroffset.z,
                self.__end.x+corneroffset.x, self.__end.y+corneroffset.y,self.__end.z+corneroffset.z,
                self.__end.x-corneroffset.x, self.__end.y-corneroffset.y, self.__end.z-corneroffset.z
            )

            # Index data for the plane. This tells the shader how to use the vertex data.
            indexdata = (
                0,1,2,
                1,3,2
            )

            # Converts the vertex and index data into a format useable by OpenGL
            self.__vertexdata = numpy.array(vertexdata, dtype=numpy.float32)
            self.__indexdata = numpy.array(indexdata, dtype=numpy.uint32)

            # Binds the shaderprogram and buffers. (Tells OpenGL that these are the shaders/buffers that we want to use to draw the ship)
            glDepthFunc(GL_LESS)
            glUseProgram(shaderlist[2])
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.__indexdata.nbytes, self.__indexdata, GL_STATIC_DRAW)
            glBufferData(GL_ARRAY_BUFFER, self.__vertexdata.nbytes, self.__vertexdata, GL_STATIC_DRAW)

            # Tells the shaders where certain attributes are in the vertexdata list.
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), c_void_p(0))
            glEnableVertexAttribArray(0)

            #Perspective and world matrix for moving the lazer to camera space.
            glUniformMatrix4fv(glGetUniformLocation(shaderlist[2], "perspectiveMatrix"), 1, GL_FALSE,
                            glm.value_ptr(perspectiveMatrix))
            glUniformMatrix4fv(glGetUniformLocation(shaderlist[2], "worldMatrix"), 1, GL_FALSE,
                            glm.value_ptr(worldMatrix))
            #This defines which colour the lazer should be.
            glUniform3fv(glGetUniformLocation(shaderlist[2],"color"), 1,
                        glm.value_ptr(self.__color))

            # Draws the Lazer to the screen.
            glDrawElements(GL_TRIANGLES, len(self.__indexdata), GL_UNSIGNED_INT, None)

    #A funcion that shows and hides the lazer
    def setvisible(self):
        self.__isvisible = True
    def setnotvisible(self):
        self.__isvisible = False

    #A static function that returns False, may be replaced.
    def getIsActor(self):
        return False

    def setpos(self,start=None,end=None):
        if start != None:
            self.__start = glm.vec4(start,1)
        if end != None:
            self.__end = glm.vec4(end,1)

class ScreenSpaceSprite:
    def __init__(self,imagefile):
        self.__translation = glm.mat4(1)
        self.__rotation = glm.mat4(1)
        self.__scale = glm.mat4(1)

        self.image = pygame.image.load(imagefile)
    def drawObj(self, worldMatrix, perspectiveMatrix,
                shaderlist,
                vertexbufferlist,
                indexbufferlist,
                parentMatrix=glm.vec4(1)
                ):

        objMatrix = parentMatrix * (self.__translation * self.__rotation * self.__scale)

        vertexdata = (
            -1.0,-1.0,0.0,0.0,0.0,
            -1.0,1.0,0.0,0.0,1.0,
            1.0, 1.0, 0.0,1.0,1.0,
            1.0,-1.0,0.0,1.0,0.0
        )

        indexdata = (
            0, 1 ,2,
            2, 3, 0
        )

        self.__vertexdata = numpy.array(vertexdata, dtype=numpy.float32)
        self.__indexdata = numpy.array(indexdata, dtype=numpy.uint32)

        # Binds the shaderprogram and buffers. (Tells OpenGL that these are the shaders/buffers that we want to use to draw the ship)
        glDepthFunc(GL_LESS)
        glUseProgram(shaderlist[3])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.__indexdata.nbytes, self.__indexdata, GL_STATIC_DRAW)
        glBufferData(GL_ARRAY_BUFFER, self.__vertexdata.nbytes, self.__vertexdata, GL_STATIC_DRAW)

        # Tells the shaders where certain attributes are in the vertexdata list.
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), c_void_p(12))
        glEnableVertexAttribArray(1)

        glUniformMatrix4fv(glGetUniformLocation(shaderlist[3], "perspectiveMatrix"), 1, GL_FALSE,
                           glm.value_ptr(perspectiveMatrix))
        glUniformMatrix4fv(glGetUniformLocation(shaderlist[3], "objectMatrix"), 1, GL_FALSE,
                           glm.value_ptr(objMatrix))

        # Draws the prop to the screen.
        glDrawElements(GL_TRIANGLES, len(self.__indexdata), GL_UNSIGNED_INT, None)
    def getIsActor(self):
        return False
