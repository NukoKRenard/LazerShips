#version 330 core
layout (location = 0) in vec3 aPos;

//Used to translate the 3D skybox into the 2D camera space
uniform mat4 perspectiveMatrix;
uniform mat4 worldMatrix;

//Defines where we should draw the cubemap
out vec3 texCoord;

void main()
{
	//Sets the position of the cubemap so that it always renders behind everything.
	gl_Position = (perspectiveMatrix*worldMatrix*vec4(aPos,0.0)).xyww;
	//Sends the texcoord to the fragment shader.
	texCoord = vec3(aPos.xy,aPos.z);

}