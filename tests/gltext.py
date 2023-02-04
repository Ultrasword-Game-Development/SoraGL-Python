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

shader = mgl.ShaderProgram("assets/shaders/testing.glsl")

vertices = mgl.Buffer('16f', [-1.0, -1.0, 0.0, 1.0,
                            1.0, -1.0, 1.0, 1.0,
                            1.0, 1.0, 1.0, 0.0,
                            -1.0, 1.0, 0.0, 0.0])
indices = mgl.Buffer('6i', [0, 1, 2, 3, 0, 2])
vattrib = mgl.VAO("assets/shaders/testing.glsl")
vattrib.add_attribute('2f', 'vvert')
vattrib.add_attribute('2f', 'vuv')
# add attribs?
vattrib.create_structure(vertices, indices)

vattrib.change_uniform("ures", SORA.WSIZE)

# ------------------------------ #
# game loop
SORA.start_engine_time()
while SORA.RUNNING:
    SORA.FRAMEBUFFER.fill((255, 255, 255, 255))
    # pygame update + render
    # print(SORA.get_mouse_abs()[0] / SORA.WSIZE[0], SORA.get_mouse_abs()[1] / SORA.WSIZE[1])

    # moderngl render
    ModernGL.update_context()
    ModernGL.CTX.clear(ModernGL.CLEARCOLOR[0], ModernGL.CLEARCOLOR[1], ModernGL.CLEARCOLOR[2], ModernGL.CLEARCOLOR[3])
    ModernGL.CTX.enable(mgl.moderngl.BLEND)
    vattrib.change_uniform("utime", SORA.ENGINE_UPTIME % 10000)
    vattrib.change_uniform("umpos", (SORA.get_mouse_abs()[0] / SORA.WSIZE[0]*2-1, -SORA.get_mouse_abs()[1] / SORA.WSIZE[1]*2+1))
    # vattrib.change_uniform("framebuffer", mgl.Texture.pg2gltex(SORA.FRAMEBUFFER, "fb"))
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

