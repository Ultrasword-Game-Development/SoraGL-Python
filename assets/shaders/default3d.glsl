###
#vertex
#version 300 es

in vec3 vvert;
in vec2 vuv;
in vec4 vcolor;

uniform mat4 view;
uniform mat4 proj;
// uniform float utime;

out vec2 fuv;
out vec4 fcolor;

void main() {
    gl_Position = proj * view * vec4(vvert, 1.0);
    // gl_Position = vec4(vvert, 1.0);
    // fuv = vuv;
    fcolor = vcolor;
}

###
#fragment
#version 300 es

in vec2 fuv;
in vec4 fcolor;

uniform float utime;
// uniform sampler2D framebuffer, debugbuffer;

out vec4 FragColor;

void main(){
    utime + 1.;
    // vec4 color = texture(framebuffer, uv);
    // vec4 debug = texture(debugbuffer, uv);
    FragColor = fcolor;
}