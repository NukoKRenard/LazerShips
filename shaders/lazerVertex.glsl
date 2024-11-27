#version 330 core
layout (location = 0) in vec3 aPos;

//Matricies used to take the object in a 3D space and translate it into the 2D camera space
uniform mat4 perspectiveMatrix;
uniform mat4 worldMatrix;

void main()
{
	//Moves the vertex into the camera space
	gl_Position = perspectiveMatrix*worldMatrix*vec4(aPos,1.0);
}
