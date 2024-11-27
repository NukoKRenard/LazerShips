#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexPos;

uniform mat4 objectMatrix;
uniform mat4 perspectiveMatrix;

out vec2 texPos;

void main() {
    gl_Position = perspectiveMatrix*objectMatrix*vec4(aPos.xy,0.0,1.0);
    texPos = aTexPos;
}
