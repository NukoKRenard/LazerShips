#version 330 core
out vec4 fragColor;

uniform vec3 color;

in vec2 texCoord;

void main() {
    fragColor = vec4(color/255.0,1.0-length(texCoord));
}
