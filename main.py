import pygame
import engine
import struct

# ------------------------------ #
# setup
SORA = engine.SoraContext.initialize({"fps": 30, "window_size": [1280, 720], 
            "window_flags": pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF, 
            "window_bits": 32, "framebuffer_flags": pygame.SRCALPHA, 
            "framebuffer_size": [1280//3, 720//3], "framebuffer_bits": 32})

SORA.create_context()

# ------------------------------ #
# import gl?
if SORA.is_flag_active(pygame.OPENGL):
    print('loaded')
    from engine import mgl
    from engine.mgl import ModernGL

# from engine import mgl
# ------------------------------ #
# post setup

ModernGL.create_context(options={"standalone": False, "gc_mode": "context_gc", "clear_color": [0.0, 0.0, 0.0, 1.0]})

shader = mgl.ShaderProgram("assets/shaders/default.glsl")

vertices = mgl.Buffer('16f', [-1.0, -1.0, 0.0, 1.0,
                            1.0, -1.0, 1.0, 1.0,
                            1.0, 1.0, 1.0, 0.0,
                            -1.0, 1.0, 0.0, 0.0])
indices = mgl.Buffer('6i', [0, 1, 2, 3, 0, 2])
vattrib = mgl.VAO()
vattrib.add_attribute('2f', 'vvert')
vattrib.add_attribute('2f', 'vuv')
# add attribs?
vattrib.create_structure(vertices, indices)


# verts = [-0.5, -0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5]
# verts_buf = struct.pack('8f', *verts)
# ind_buf = struct.pack('6i', *[0, 1, 2, 
#                                 3, 0, 2])
# vbo = ModernGL.CTX.buffer(verts_buf)
# ibo = ModernGL.CTX.buffer(ind_buf)
# vao = ModernGL.CTX.vertex_array(shader.program, [(vbo, '2f', 'vvert')], ibo)


"""
TODO:
4. cleaning up buffers --> releasing all gl context data

ERRORS:
1. resizing window increases RAM usage -- maybe opengl error? gc?
"""

image = SORA.load_image("assets/sprites/tomato.png")

# ------------------------------ #
# game loop
SORA.start_engine_time()
while SORA.RUNNING:
    SORA.FRAMEBUFFER.fill((255, 255, 255, 255))
    # pygame update + render
    pygame.draw.rect(SORA.FRAMEBUFFER, (255, 0, 0), pygame.Rect(0, 0, 100, 100))
    SORA.FRAMEBUFFER.blit(image, (100, 100))

    # moderngl render
    ModernGL.update_context()
    ModernGL.CTX.clear(ModernGL.CLEARCOLOR[0], ModernGL.CLEARCOLOR[1], ModernGL.CLEARCOLOR[2], ModernGL.CLEARCOLOR[3])
    ModernGL.CTX.enable(mgl.moderngl.BLEND)
    vattrib.change_uniform("utime", SORA.ENGINE_UPTIME % 10000)
    vattrib.change_uniform("framebuffer", mgl.Texture.pg2gltex(SORA.FRAMEBUFFER, "fb"))
    # print(vattrib.uniforms)

    # vao.render(mode=mgl.moderngl.TRIANGLES)
    vattrib.render()
    ModernGL.CTX.disable(mgl.moderngl.BLEND)
    
    # push frame
    # SORA.push_framebuffer()
    pygame.display.flip()
    # update events
    SORA.update_hardware()
    SORA.handle_pygame_events()
    # clock tick
    SORA.CLOCK.tick(SORA.FPS)
    SORA.update_time()

pygame.quit()

