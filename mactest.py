import pygame
import engine
import struct

from engine import animation, scene, physics, base_objects

# ------------------------------ #
# setup
SORA = engine.SoraContext.initialize({"fps": 30, "window_size": [1280, 720], 
            "window_flags": pygame.RESIZABLE | pygame.DOUBLEBUF, 
            "window_bits": 32, "framebuffer_flags": pygame.SRCALPHA, 
            "framebuffer_size": [1280//3, 720//3], "framebuffer_bits": 32})

SORA.create_context()

# ------------------------------ #


animation.Category.load_category("assets/sprites/tomato.json")
registry = animation.Category.get_category_framedata("assets/sprites/tomato.json")["idle"].get_registry()

"""
TODO:
4. cleaning up buffers --> releasing all gl context data

ERRORS:
1. resizing window increases RAM usage -- maybe opengl error? gc?
2. 

TODO v2:
1. make more components + aspects (they come in pairs btw)
2. start finalizing scene / layer system
3. figure out chunks
"""

image = SORA.load_image("assets/sprites/tomato.png")
__ss = animation.SpriteSheet(SORA.load_image("assets/sprites/stages.png"), 16, 16, 0, 0)

sc = scene.Scene()
scw = scene.World()
sc.add_layer(scw, 0)
sce1 = physics.Entity()
sce2 = physics.Entity()

# add entities to world first
scw.add_entity(sce1)
scw.add_entity(sce2)


# entity comp
sce1.add_component(base_objects.MovementComponent(1, 0.3))
sce1.add_component(base_objects.Collision2DComponent(10, 10))

sce2.add_component(base_objects.MovementComponent(2, 0.1))
sce2.add_component(base_objects.Collision2DComponent(10, 10))


# aspects
scw.add_aspect(base_objects.MovementAspect())
scw.add_aspect(base_objects.Collision2DAspect())

scene.SceneHandler.push_scene(sc)

# ------------------------------ #
# game loop
SORA.start_engine_time()
while SORA.RUNNING:
    SORA.FRAMEBUFFER.fill((255, 255, 255, 255))
    # pygame update + render
    scene.SceneHandler.update()

    pygame.draw.rect(SORA.FRAMEBUFFER, (255, 0, 0), pygame.Rect(0, 0, 100, 100))
    SORA.FRAMEBUFFER.blit(image, (100, 100))
    
    for i, spr in enumerate(__ss):
        pygame.draw.rect(SORA.FRAMEBUFFER, (255, 100, 100), pygame.Rect((i*16 + 200, 30), spr.get_frame().get_size()))
        SORA.FRAMEBUFFER.blit(spr.get_frame(), (i*16 + 200, 30))

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

