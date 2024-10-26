#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNorm;
layout (location = 2) in vec2 aTexPos;

uniform mat4 objMatrix;
uniform mat4 perspectiveMatrix;
uniform mat4 worldMatrix;

out vec4 normal;
out vec2 texCoord;

void main()
{
	gl_Position = perspectiveMatrix*worldMatrix*objMatrix*vec4(aPos,1.0);
	normal = (objMatrix*vec4(aNorm,0.0))/length((objMatrix*vec4(aNorm,0.0)));
	texCoord = vec2(aTexPos.x,aTexPos.y);
}
