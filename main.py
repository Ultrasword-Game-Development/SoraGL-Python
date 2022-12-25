import pygame
import engine
import struct

# ------------------------------ #
# setup



SORA = engine.SoraContext.initialize({"fps": 30, "window_size": [1280, 720], 
            "window_flags": pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF, 
            "window_bits": 32, "framebuffer_flags": pygame.SRCALPHA, 
            "framebuffer_size": [1280, 720], "framebuffer_bits": 32})

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

verts = [0.0, 0.5, -0.5, -0.5, 0.5, -0.5]
verts_buf = struct.pack('6f', *verts)
ind_buf = struct.pack('6i', *[0, 1, 2, 
                                2, 1, 3])
vbo = ModernGL.CTX.buffer(verts_buf)
ibo = ModernGL.CTX.buffer(ind_buf)
vao = ModernGL.CTX.vertex_array(shader.program, [(vbo, '2f', 'vvert')], ibo)

"""
TODO:
1. ipmlement uniform uploading --> textures, times, uniform values  basically
2. let me  push frame buffer to gl screen context!
3. start rendering to frambuffer /implement new game engine system! -- OUTLINE ON DOC FIRST
4. etc
"""


# ------------------------------ #
# game loop
while SORA.RUNNING:
    SORA.FRAMEBUFFER.fill((255, 255, 255, 255))
    # update + render
    ModernGL.update_context()
    ModernGL.CTX.clear(ModernGL.CLEARCOLOR[0], ModernGL.CLEARCOLOR[1], ModernGL.CLEARCOLOR[2], ModernGL.CLEARCOLOR[3])
    ModernGL.CTX.enable(mgl.moderngl.BLEND)
    vao.render(mode=mgl.moderngl.TRIANGLES)
    ModernGL.CTX.disable(mgl.moderngl.BLEND)
    
    # push frame
    SORA.push_framebuffer()
    # update events
    SORA.update_hardware()
    SORA.handle_pygame_events()
    # clock tick
    SORA.CLOCK.tick(SORA.FPS)

pygame.quit()

