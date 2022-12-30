import pygame
import engine
import struct

from engine import animation

# ------------------------------ #
# setup
SORA = engine.SoraContext.initialize({"fps": 30, "window_size": [1280, 720], 
            "window_flags": pygame.RESIZABLE | pygame.DOUBLEBUF, 
            "window_bits": 32, "framebuffer_flags": pygame.SRCALPHA, 
            "framebuffer_size": [1280//3, 720//3], "framebuffer_bits": 32})

SORA.create_context()

# ------------------------------ #


animation.Category.load_category("assets/sprites/tomato.json")
registry = animation.Category.get_category_framedata("assets/sprites/tomato.json")["default"].get_registry()


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

    registry.update()
    pygame.draw.rect(SORA.FRAMEBUFFER, (0, 0, 255), pygame.Rect((200, 120), registry.get_frame().get_size()))
    SORA.FRAMEBUFFER.blit(registry.get_frame(), (200, 120))
    
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

