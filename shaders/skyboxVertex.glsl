#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 perspectiveMatrix;
uniform mat4 worldMatrix;

out vec3 texCoord;

void main()
{
	gl_Position = (perspectiveMatrix*worldMatrix*vec4(aPos,0.0)).xyww*100;
	texCoord = vec3(aPos.xy,aPos.z);

}