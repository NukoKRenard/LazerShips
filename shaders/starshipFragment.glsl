#version 330 core
out vec4 fragColor;

uniform mat4 objMatrix;
uniform mat4 worldMatrix;

uniform vec3 lightPos;
uniform sampler2D colourMap;
uniform sampler2D glowMap;
uniform samplerCube reflection;

in vec4 normal;
in vec2 texCoord;
in vec3 position;

void main()
{
    vec4 camera_pos = inverse(worldMatrix)*vec4(0,0,0,1);
    vec4 basetexture = texture(colourMap,texCoord);
    vec4 littexture = clamp(basetexture*dot(normal.xyz,lightPos),0,1) + texture(colourMap,texCoord)*texture(glowMap,texCoord).g;
    vec4 highlightedtexture = littexture + vec4(clamp(pow(dot(normalize(camera_pos.xyz-position),normalize(reflect(lightPos,normal.xyz))),10),0,1))*texture(glowMap,texCoord).r;
    vec4 reflectedtexture = highlightedtexture+clamp(texture(reflection,reflect(camera_pos.xyz-position,normal.xyz))*texture(glowMap,texCoord).r,0,1);

    fragColor = reflectedtexture;
}
