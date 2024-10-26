import pygame
from OpenGL.GL import *
from ctypes import c_void_p
import numpy
import glm
from math import *

#The problematic code is somewhere in this function.
class Model:
    def __init__(self, ObjFilePath, TexFilePath,ID,shaderID = 0):
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
                print(f"{ID}: {databit}")
                databitlist = databit.split(' ')[1:]
                print(databitlist)
                databitlistconverted = []
                for value in databitlist:
                    databitlistconverted.append(float(value))
                print(databitlistconverted)
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
                    if face.strip() not in alreadymadevertdata:
                        alreadymadevertdata.append(face.strip())


                        indexes = face.split('/')
                        for vert in vertpos[int(indexes[0]) - 1]:
                            vertexdata.append(vert)
                        try:
                            for norm in normpos[int(indexes[1]) - 1]:
                                vertexdata.append(norm)
                        #If the normal value is blank, it will fill the spaces with blank values
                        except:
                            vertexdata.append(0.0)
                            vertexdata.append(0.0)
                            vertexdata.append(0.0)
                            print(f"Tex normal for face {databitlist} was not found.")
                        try:
                            for tex in texpos[int(indexes[2]) - 1][:2]:
                                vertexdata.append(tex)
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
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        textureData = pygame.image.load(TexFilePath).convert_alpha()
        #Flips the texture, for some reason pygame loads them in upside down so this needs to happen
        pygame.transform.flip(textureData,False,True)
        image_width, image_height = textureData.get_rect().size
        image = pygame.image.tobytes(textureData,"RGBA")
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,image)
        glGenerateMipmap(GL_TEXTURE_2D)

    #A function to call to prepare the texture to be drawn.
    def bindTexture(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def getVertexData(self):
        return self.__vertexdata
    def getIndexData(self):
        return self.__indexdata
    def getShader(self):
        return self.__shaderID

#This is the end of the problematic funcion. The isse may also be in the main Program() class

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

            print(cubeimagefilepaths[i],image_width,image_height)
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





class Program:
    def __init__(self):
        pygame.init()
        self.deltaTime = 1/60
        pygame.mouse.set_visible(False)
        self.__clock = pygame.time.Clock()
        self.models = []
        self.userhasquit = False
        self.maincam = Camera(45)

        #Loads actors into a list of objects to be drawn to the screen.
        self.models.append(Model("levelobjects/AvaxInterceptor.obj", "levelobjects/texturedata/AvaxInterceptorColourMap.png", "ship-model"))
        self.models.append(Skybox("skybox","space-skybox"))

        #This is an error colour to show if something was not dran, this should ideally never be seen on the screen.
        glClearColor(1.0, 0.0, 1.0, 1)

        while not self.userhasquit:
            events = pygame.event.get()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            #The code below rotates the object in accordance with delta time, it has been disabled for debugging
            #self.models[0].objMatrix *= glm.rotate((1/60)*self.deltaTime,(0,1,0))

            for event in events:
                if event.type == pygame.QUIT:
                    self.userhasquit = True
                    break

            #Updates the cameras position based on userinput
            #NOTE as of this stage userinput is crude. Movement directions to not account for the look direction.
            self.maincam.updateCamera(self.deltaTime)
            #This function loops through all of the objects in the prop list and draws them with the drawObj() function
            self.maincam.renderScene(self.models)

            pygame.display.flip()
            self.__clock.tick(60)
            if (self.__clock.get_fps()/60) != 0:
                self.deltaTime = 1/(self.__clock.get_fps()/60)
            else:
                self.deltaTime = 0






Program()