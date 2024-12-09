#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;

//The position, rotation, and scale of the object in the world.
uniform mat4 objectMatrix;

//Two matricies used to move the object from 3D world space into the 2D camera clip space.
uniform mat4 perspectiveMatrix;
uniform mat4 worldMatrix;

out vec2 texCoord;

void main() {
    gl_Position = perspectiveMatrix*worldMatrix*objectMatrix*vec4(aPos,1.0);
    texCoord = aTexCoord;
}
