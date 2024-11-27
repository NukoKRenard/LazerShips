#version 330 core
out vec4 fragColor;

//The colour uniform sent to the shader
uniform vec3 color;

void main()
{
    //Sets the colour of the pixel to the colour we passed to the uniform.
    fragColor = vec4(color,1);
}
