#version 330 core
out vec4 fragColor;

//The direction that we should sample from the texture.
in vec3 texCoord;

//The cubemap texture we will sample
uniform samplerCube skyboxTexture;

void main()
{
    //Sets the colour of the fragment to be the sampled texture we got from the camera. Basically asks "Which pixel on the cubemap to we draw to the pixel on the camera?"
    fragColor = vec4(texture(skyboxTexture,texCoord).xyz,1.0);
}
