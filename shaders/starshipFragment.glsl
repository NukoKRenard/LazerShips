#version 330 core
out vec4 fragColor;

uniform mat4 objMatrix;

uniform vec3 lightPos;
uniform sampler2D colourMap;
uniform sampler2D glowMap;

in vec4 normal;
in vec2 texCoord;

void main()
{
    fragColor = texture(colourMap,texCoord)*min(dot(normal.xyz,lightPos)+texture(glowMap,texCoord),1.0);
}
