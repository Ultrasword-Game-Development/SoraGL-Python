###
#vertex
#version 300 es

in vec2 vvert;
in vec2 vuv;
// in vec3 vcolor;

// uniform float utime;

out vec2 fuv;

void main() {
    gl_Position = vec4(vvert, 0.0, 1.0);
    fuv = vuv;
}

###
#fragment
#version 300 es

in vec2 fuv;

uniform float utime;
uniform sampler2D framebuffer;

void main(){
    vec4 texcol = texture(framebuffer, fuv);
    utime * 2;
    vec4 col = vec4(fuv.x, 1.0, 1.0, 1.0);
    gl_FragColor = texcol;
}