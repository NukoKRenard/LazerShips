#version 330 core
out vec4 fragColor;

uniform mat4 objMatrix;

uniform vec3 lightPos;
uniform sampler2D colourMap;

in vec4 normal;
in vec2 texCoord;

void main()
{
    fragColor = texture(colourMap,texCoord);//*dot(normal.xyz,lightPos);//vec4(texture(colourMap,texCoord).xyz,0.0)*dot(lightPos,normal.xyz);
}
