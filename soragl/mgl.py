import soragl
if soragl.SoraContext.DEBUG:
    print("Activated mgl.py")

import glm

from . import misc
import moderngl

import struct
from array import array

import pygame.math as pgmath


class ModernGL:
    # ------------------------------ #
    # modern gl globals
    CTX = None
    CLEARCOLOR = [0.0, 0.0, 0.0, 1.0]

    # ------------------------------ #
    # static
    FB_BUFFER = None

    # ------------------------------ #
    @classmethod
    def create_context(cls, options: dict):
        """Creates moderngl context."""
        cls.CTX = moderngl.create_context(options['standalone'])
        cls.CTX.gc_mode = options['gc_mode'] if 'gc_mode' in options else None
        cls.CLEARCOLOR = options['clear_color'] if 'clear_color' in options else ModernGL.CLEARCOLOR
        # create the quad buffer for FB
        print("quad buffer needs to be replaced with custom vao object")
        cls.FB_BUFFER = cls.CTX.buffer(data = array('f', [
            -1.0, -1.0,     0.0, 0.0,
            1.0, -1.0,      1.0, 0.0,
            1.0, 1.0,       1.0, 1.0,
            -1.0, 1.0,      0.0, 1.0,
        ]))
        # stuff
        if options["depth_test"]: cls.CTX.enable(moderngl.DEPTH_TEST)

    @classmethod
    def update_context(cls):
        """Updates moderngl context."""
        
        # garbage collection
        cls.CTX.gc()

    @classmethod
    def render(cls, texture):
        """Renders the framebuffer to the window."""
        # render frame buffer texture to window!
        cls.CTX.screen.use()
        cls.CTX.enable(moderngl.BLEND)
        cls.CTX.clear(ModernGL.CLEARCOLOR[0], ModernGL.CLEARCOLOR[1], ModernGL.CLEARCOLOR[2], ModernGL.CLEARCOLOR[3])
        
        
        cls.CTX.disable(moderngl.BLEND)
    
    @classmethod
    def set_clear_color(cls, color):
        """Sets the clear color."""
        cls.CLEARCOLOR = color


# ------------------------------ #
# textures

class Texture:
    """
    Texture class
    - handles textures, pygame to gltex conversion, loading textures, etc
    """

    def __init__(self, path: str, pos: list, size: list=None, scale:list=None):
        """Create Texture object"""
        self.path = path
        self.pos = pos
        self.size = size
        self.scale = scale
        self.sprite = Texture.load_texture(self.path)
        if not self.size and not self.scale:
            # assume original size
            self.scale = [1, 1]
            self.size = list(self.sprite.get_size())
        elif self.size:
            self.sprite = soragl.SoraContext.scale_image(self.sprite, self.size)
        elif self.scale:
            self.size = list(self.sprite.get_size())
            self.sprite = soragl.SoraContext.scale_image(self.sprite, (self.size[0] * self.scale[9], self.size[1] * self.scale[1]))
        # texture is now loaded + scaled if required
    
    def use(self, location=0):
        """Use the texture"""
        self.sprite.use(location=location)

    def get_size(self):
        """Get the size of the texture"""
        return self.size
    
    def get_pos(self):
        """Get the position of the texture"""
        return self.pos
    
    def get_scale(self):
        """Get the scale of the texture"""
        return self.scale

    # ------------------------------ #
    TEXTURES = {}

    @classmethod
    def load_texture(cls, path):
        """Loads a moderngl texture from a file."""
        surf = soragl.SoraContext.load_image(path)
        return cls.pg2gltex(surf, path)

    @classmethod
    def pg2gltex(cls, surface, texname):
        """Converts pygame surface to moderngl texture."""
        c = 4
        if texname not in cls.TEXTURES:
            ntex = ModernGL.CTX.texture(surface.get_size(), c)
            ntex.filter = (moderngl.NEAREST, moderngl.NEAREST)
            ntex.swizzle = 'BGRA' # TODO - swapped this
            cls.TEXTURES[texname] = ntex
        # upload texture data to GPU
        tdata = surface.get_view('1')
        cls.TEXTURES[texname].write(tdata)
        return cls.TEXTURES[texname]

# ------------------------------ #
# shaders

class ShaderStep:
    """
    Shader Steps!!!
    - vertex or fragment for now
    """
    VERTEX = 0
    FRAGMENT = 1

    SNIPPETS = ["#vertex", "#fragment"]

    def __init__(self, shadersnippet: str):
        """Stores data for shaderstep"""
        # determine what type of shader it is
        pre = shadersnippet.split('\n')[1:][:-1]
        if pre[0] not in self.SNIPPETS:
            raise Exception("Invalid shader snippet")
        self.shadertype = self.SNIPPETS.index(pre[0])
        self.shader = shadersnippet[len(self.SNIPPETS[self.shadertype])+2:]

class ShaderProgram:
    """
    Takes input file.glsl and compiles it into a shader program.
    - Single file format!
    """

    PIPELINE_SPLIT = "###"

    def __init__(self, path):
        self.path = path
        # extract vert + frag shaders
        data = misc.fread(path)
        # separate into Vertex and Fragment shaders
        self.sections = [ShaderStep(shadersnippet) for shadersnippet in data.split(ShaderProgram.PIPELINE_SPLIT)[1:]]
        self.sections.sort(key=lambda x: x.shadertype)
        # create program
        print(self.path)
        self.program = ModernGL.CTX.program(vertex_shader=self.sections[0].shader, fragment_shader=self.sections[1].shader)
    
    def update_uniforms(self, s: str, uniforms: dict):
        """Update uniforms"""
        tcount = 0
        shader = ShaderProgram.SHADERS[s]
        for uni in uniforms:
            # check if texture type
            try:
                # print(uniforms[uni], type(uniforms[uni]))
                if type(uniforms[uni][0]) == moderngl.texture.Texture:
                    uniforms[uni][0].use(location=tcount)
                    shader.program[uni].value = tcount
                    tcount += 1
                elif uniforms[uni][1] == VAO.SCALAR:
                    shader.program[uni].value = uniforms[uni][0]
                elif uniforms[uni][1] == VAO.VECTOR:
                    shader.program[uni].write(uniforms[uni][0])
                else:
                    print('bad uniform type')
            except Exception as e:
                print(f"Error occured when uploading uniform: `{uni}` | of value: {uniforms[uni]}")
                print(e)
                soragl.SoraContext.pause_time(0.4)

    # ------------------------------ #
    # loading shaders
    SHADERS = {}
    DEFAULT = "assets/shaders/default.glsl"

    @classmethod
    def load_shader(cls, path=None):
        """Load a shader into gl"""
        if not path:
            return cls.load_shader(cls.DEFAULT)
        if path in cls.SHADERS:
            return cls.SHADERS[path]
        cls.SHADERS[path] = ShaderProgram(path)
        return cls.SHADERS[path]


# ------------------------------ #
# buffers!

class Buffer:
    """
    Buffer class
    - handles buffers = vao, vbo, ibo, buffers!
    """

    def __init__(self, parse: str, data: list):
        """Create a Buffer object"""
        self.rawbuf = data.copy()
        self.parse = parse
        packed = struct.pack(parse, *self.rawbuf)
        # create ctx buffer
        self.buffer = ModernGL.CTX.buffer(packed)

class VAO:
    """
    Vertex Attribute Objects
    - very useful -- layout for vertices in the opengl context
    """
    SCALAR = 0
    VECTOR = 1

    def __init__(self, shader_path: str = ShaderProgram.DEFAULT):
        """Creates an empty VAO"""
        self.attributes = []
        self.vbo = None
        self.ibo = None
        self.vao = None
        self.uniforms = {}
        self.shader = shader_path
        # load the shader in mgl context
        ShaderProgram.load_shader(shader_path)
        self.initialized = False

    def add_attribute(self, parse: str, var_name: str):
        """Add an attribute to the vao"""
        self.attributes.append([parse, var_name])
    
    def change_uniform_scalar(self, name: str, value):
        """Change a uniform value"""
        self.uniforms[name] = (value, self.SCALAR)
    
    def change_uniform_vector(self, name: str, value):
        """Change a uniform value"""
        self.uniforms[name] = (value, self.VECTOR)

    def get_uniform(self, name: str):
        """Get a uniform value"""
        return self.uniforms[name]

    def create_structure(self, vbo, ibo):
        """Creates the gl context for the vao"""
        self.vbo = vbo
        self.ibo = ibo
        self.glvbo = self.vbo.buffer
        self.glibo = self.ibo.buffer
        # create the v attrib string
        blob = []
        vattrib = ' '.join([i[0] for i in self.attributes])
        blob.append(tuple([self.glvbo, vattrib] + list(i[1] for i in self.attributes)))
        self.vao = ModernGL.CTX.vertex_array(ShaderProgram.SHADERS[self.shader].program, 
                            blob,
                            self.glibo)
        self.initialized = True
        # done?
    
    def render(self, mode=moderngl.TRIANGLES):
        """Render the vao given its data"""
        if not self.initialized:
            raise Exception("VAO has not yet been initialized!")
        # update uniform variables!
        ShaderProgram.SHADERS[self.shader].update_uniforms(self.shader, self.uniforms)
        self.vao.render(mode=mode)


# ------------------------------ #
# camera

class Camera:
    def __init__(self, pos, front, up):
        # private
        self._position = glm.vec3(pos[0], pos[1], pos[2])
        self._front = glm.vec3(front[0], front[1], front[2])
        self._up = glm.vec3(up[0], up[1], up[2])

        self._view = None
        self._proj = None
    
    def calculate_view_matrix(self, pos, front, up):
        """Calculate the view matrix"""
        # add rotation
        return glm.lookAt(pos, pos + front, up)
        
    def get_view_matrix(self):
        """Get the view matrix"""
        return self._view
    
    def get_projection_matrix(self):
        """Get the projection matrix"""
        return self._proj
    
    @property
    def position(self):
        return self._position
    
    @property
    def target(self):
        return self._target

    @property
    def up(self):
        return self._up

    def translate(self, x, y, z):
        self._position += glm.vec3(x, y, z)
        self._view = self.calculate_view_matrix(self._position, self._front, self._up)


