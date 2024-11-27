#version 330 core
out vec4 fragColor;

in vec2 texPos;
uniform sampler2D image;

void main() {
    fragColor = texture(image,texPos);
}
