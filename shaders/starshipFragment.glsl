#version 330 core
out vec4 fragColor;

//The position, rotation, and scale of the object in the world.
uniform mat4 objMatrix;
//The matrix to move the object to camera view.
uniform mat4 worldMatrix;

//The direction the light is coming from in the scene (basically where is the sun)
uniform vec3 lightPos;
//The coloured texture that we draw to the screen (ships have two, a red and blue texture)
uniform sampler2D colourMap;
//This texture defines how lighting should behave, what parts of the ship should texture (like engines), and wwhich parts should reflect more or less light. This data is passed through different colour channels.
uniform sampler2D glowMap;
//This is the same cubemap we pass into the skybox. The only difference is we bind it into a different buffer.
uniform samplerCube reflection;

//The normal of the pixel in 3D space.
in vec4 normal;
//What part of the textures this pixel represents.
in vec2 texCoord;
//The 3D position of the pixel.
in vec3 position;

void main()
{
    //Gets the position of the camera relative to the origin (0,0,0)
    vec4 camera_pos = inverse(worldMatrix)*vec4(0,0,0,1);
    //This finds the base colour of the pixel due to its texutre (for example if the pixel were part of the engine flame it would appear orange)
    vec4 basetexture = texture(colourMap,texCoord);
    //This calculated the darkness value of the pixel based off of how close to the light it is facing (if it faces towards the light it would be bright, if it faces away from the light it will be dark.)
    //This line will also add a texture to the texture, where (for example with the engine flame) we don't want them to darken with light as they would produce their own. Glow data is passed through the green channel.
    vec4 littexture = clamp(basetexture*dot(normal.xyz,lightPos),0,1) + texture(colourMap,texCoord)*texture(glowMap,texCoord).g;
    //This calculates the white highlights in the texture. This is the white shine we see on points that reflect the light of the sun.
    //To calculate this we take the camera's position, reflect it across the surface of the ship, and find how close it is to the light source. The closer the brighter.
    vec4 highlights =vec4(clamp(pow(dot(normalize(camera_pos.xyz-position),normalize(reflect(lightPos,normal.xyz))),10),0,1))*texture(glowMap,texCoord).r;
    //This function generates how the sky we see reflects on the ships hull. We reflect the camera's position on the surface of the ship, and then sample the cubemap using that.
    vec4 reflections = clamp(texture(reflection,reflect(camera_pos.xyz-position,normal.xyz))*texture(glowMap,texCoord).r,0,1);

    //Takes all of what we just calculated and sends it to the pixel.
    fragColor = vec4((littexture+highlights+reflections).xyz,1.0);
}
