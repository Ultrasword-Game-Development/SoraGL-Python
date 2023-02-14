###
#vertex
#version 300 es

in vec3 vvert;
in vec2 vuv;
in vec4 vcolor;
in float vtex;

uniform mat4 view;
uniform mat4 proj;
// uniform float utime;

out vec2 fuv;
out vec4 fcolor;
out float ftex;

void main() {
    gl_Position = proj * view * vec4(vvert, 1.0);
    // gl_Position = vec4(vvert, 1.0);
    fuv = vuv;
    fcolor = vcolor;
    ftex = vtex;
}

###
#fragment
#version 300 es

in vec2 fuv;
in vec4 fcolor;
in float ftex;

uniform float utime;
// uniform sampler2D framebuffer, debugbuffer;
uniform sampler2D[9] uarray;

out vec4 FragColor;

vec4 color;

void main(){
    utime + 1.;
    // vec4 color = texture(framebuffer, uv);
    // vec4 debug = texture(debugbuffer, uv);
    // color = texture(uarray[(int)ftex], fuv.xy);
    color = texture(uarray[1], fuv);
    if (color.a <= 0.01) discard;
    // FragColor = fcolor * color;
    FragColor = color;
}