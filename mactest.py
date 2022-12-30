import pygame
import engine
import struct

# ------------------------------ #
# setup
SORA = engine.SoraContext.initialize({"fps": 30, "window_size": [1280, 720], 
            "window_flags": pygame.RESIZABLE | pygame.DOUBLEBUF, 
            "window_bits": 32, "framebuffer_flags": pygame.SRCALPHA, 
            "framebuffer_size": [1280//3, 720//3], "framebuffer_bits": 32})

SORA.create_context()

# ------------------------------ #
# import gl?
# if SORA.is_flag_active(pygame.OPENGL):
#     print('loaded')
#     from engine import mgl
#     from engine.mgl import ModernGL


# ------------------------------ #
# post setup

# ModernGL.create_context(options={"standalone": False, "gc_mode": "context_gc", "clear_color": [0.0, 0.0, 0.0, 1.0]})

# shader = mgl.ShaderProgram("assets/shaders/default.glsl")

# vertices = mgl.Buffer('16f', [-1.0, -1.0, 0.0, 1.0,
#                             1.0, -1.0, 1.0, 1.0,
#                             1.0, 1.0, 1.0, 0.0,
#                             -1.0, 1.0, 0.0, 0.0])
# indices = mgl.Buffer('6i', [0, 1, 2, 3, 0, 2])
# vattrib = mgl.VAO()
# vattrib.add_attribute('2f', 'vvert')
# vattrib.add_attribute('2f', 'vuv')
# # add attribs?
# vattrib.create_structure(vertices, indices)


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
    
    # push frame
    SORA.push_framebuffer()
    # pygame.display.flip()
    # update events
    SORA.update_hardware()
    SORA.handle_pygame_events()
    # clock tick
    SORA.CLOCK.tick(SORA.FPS)
    SORA.update_time()

pygame.quit()

