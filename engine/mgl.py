import engine
from . import misc
import moderngl

from array import array


class ModernGL:
    # ------------------------------ #
    # modern gl globals
    CTX = None
    CLEARCOLOR = [0.0, 0.0, 0.0, 1.0]

    TEXTURES = {}
    SHADERS = {}
    VAOS = {}

    # ------------------------------ #
    # static
    FB_BUFFER = None

    # ------------------------------ #
    @classmethod
    def create_context(cls, options: dict):
        """Creates moderngl context."""
        cls.CTX = moderngl.create_context(options['standalone'])
        cls.CTX.gc_mode = options['gc_mode']
        cls.CLEARCOLOR = options['clear_color']
        # create the quad buffer for FB
        cls.FB_BUFFER = cls.CTX.buffer(data = array('f', [
            -1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
            -1.0, 1.0, 0.0, 1.0,
        ]))

    @classmethod
    def update_context(cls):
        """Updates moderngl context."""
        
        # garbage collection
        cls.CTX.gc()

    @classmethod
    def render(cls):
        """Renders the framebuffer to the window."""
        # render frame buffer texture to window!
        cls.CTX.screen.use()
        cls.CTX.screen.clear(cls.CLEARCOLOR)
        cls.CTX.screen.blit(cls.FB_BUFFER, (0, 0, 0, 0), cls.FB_BUFFER.size)



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
        sections = [ShaderStep(shadersnippet) for shadersnippet in data.split(ShaderProgram.PIPELINE_SPLIT)[1:]]
        sections.sort(key=lambda x: x.shadertype)
        # create program
        self.program = ModernGL.CTX.program(vertex_shader=sections[0].shader, fragment_shader=sections[1].shader)
    
    def bind(self):
        """Use this shader program"""
        self.program.use()
    
    def unbind(self):
        """Stop using this shader program"""
        self.program.release()


# ------------------------------ #

class Texture:
    """
    Texture class
    - handles textures, pygame to gltex conversion, loading textures, etc
    """

    @classmethod
    def load_texture(cls, path, name):
        """Loads a moderngl texture from a file."""
        surf = engine.SoraContext.load_image(path)
        cls.pg2gltex(surf, name)

    @classmethod
    def pg2gltex(cls, surface, texname):
        """Converts pygame surface to moderngl texture."""
        c = 4
        if texname not in cls.TEXTURES:
            ntex = cls.CTX.texture(surface.get_size(), c)
            ntex.filter = (moderngl.NEAREST, moderngl.NEAREST)
            ntex.swizzle = 'BGRA'
            cls.TEXTURES[texname] = ntex
        # upload texture data to GPU
        tdata = surface.get_view('1')
        cls.TEXTURES[texname].write(tdata)

