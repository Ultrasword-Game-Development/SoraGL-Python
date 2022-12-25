###
#vertex
#version 330

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
#version 330

in vec2 fuv;

uniform float utime;
uniform sampler2D framebuffer;

void main(){
    gl_FragColor = vec4(fuv.x, fuv.y * sin(utime), 1.0, 1.0);
    vec4 col = texture(framebuffer, fuv);
}