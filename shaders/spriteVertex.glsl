#version 330 core
layout (location=0) in vec2 aPos;
layout (location=1) in vec2 aTexPos;
out vec2 texCoord;

uniform mat4 objMatrix;
uniform mat4 perspectiveMatrix;

void main() {
    gl_Position = perspectiveMatrix*objMatrix*vec4(aPos,-1.0,1.0);
    texCoord = aTexPos;

}