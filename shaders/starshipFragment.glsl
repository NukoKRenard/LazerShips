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
    vec4 basetexture = texture(colourMap,texCoord);
    vec4 shadedtexture = basetexture*dot(normal.xyz,lightPos) + texture(colourMap,texCoord)*texture(glowMap,texCoord).g;

    fragColor = shadedtexture;
}
