#version 330
in vec2 texPos;

uniform sampler2D image;
uniform float greyscale=0.0;

void main() {
    vec4 greyscaleimage = vec4(vec3(length(texture(image,texPos).xyz)),1.0);
    gl_FragColor = texture(image,texPos)*(1.0-greyscale) + greyscaleimage*greyscale;
}
