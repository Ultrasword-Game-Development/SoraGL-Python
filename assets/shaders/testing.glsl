###
#vertex
#version 330

layout (location=0) in vec2 vvert;
layout(location=1) in vec2 vuv;
// in vec3 vcolor;

// uniform float utime;

out vec2 fuv;
out vec2 fvert;

void main() {
    gl_Position = vec4(vvert, 0.0, 1.0);
    fuv = vuv;
    fvert = vvert;
}

###
#fragment
#version 330

in vec2 fuv;
in vec2 fvert;

uniform float utime;
uniform ivec2 ures;
uniform vec2 umpos;

vec3 color = vec3(1.0);

void main(){
    ures;
    // using the mpos on screen - we can draw a circle that is within the range of it
    if (length(fvert - umpos) < 0.1) {
        color = vec3(sin(utime), cos(utime), 0.0);
        color = vec3(umpos, 0.0);
    }
    gl_FragColor = vec4(color, 1.0);
}