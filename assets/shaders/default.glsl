###
#vertex
#version 330

in vec2 vvert;
// in vec3 vcolor;

out vec3 fcolor;

void main() {
    gl_Position = vec4(vvert, 0.0, 1.0);
    fcolor = gl_Position.xyz + vec3(0.5, 0.5, 0.5);
}

###
#fragment
#version 330

in vec3 fcolor;

void main(){
    gl_FragColor = vec4(fcolor, 1.0);
}