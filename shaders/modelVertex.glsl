#version 330 core
//The position of the vertex in 3D space
layout (location = 0) in vec3 aPos;
//The direction the triangle is facing as a 3 component vector.
layout (location = 1) in vec3 aNorm;
//The coordinate on the 2D texture that this vertex represents. (The fragment shader automatically interpolates this data, generating a gradient that can be used to sample different values for each pixel.)
layout (location = 2) in vec2 aTexPos;

//The position, rotation, and scale of the object in the world.
uniform mat4 objMatrix;

//Two matricies used to move the object from 3D world space into the 2D camera clip space.
uniform mat4 perspectiveMatrix;
uniform mat4 worldMatrix;

//Outputs data to the fragment shader for lighting calculations.
out vec4 normal;
out vec2 texCoord;
out vec3 position;

void main()
{
	//Moves the vertex to the proper position on the screen.
	gl_Position = perspectiveMatrix*worldMatrix*objMatrix*vec4(aPos,1.0);

	///Sends all of this data to the fragment shader.
	normal = (objMatrix*vec4(aNorm,0.0))/length((objMatrix*vec4(aNorm,0.0)));
	texCoord = vec2(aTexPos.x,aTexPos.y);
	position = (objMatrix*vec4(aPos,1)).xyz;
}
