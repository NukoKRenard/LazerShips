#version 330 core
out vec4 fragColor;

in vec3 texCoord;

uniform samplerCube skyboxTexture;

void main()
{
    fragColor = vec4(texture(skyboxTexture,texCoord).xyz,1.0);
}
