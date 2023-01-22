import pygame
import soragl
import struct

from pygame import draw as pgdraw
from pygame import math as pgmath
from soragl import animation, scene, physics, base_objects

# ------------------------------ #
# setup
SORA = soragl.SoraContext.initialize({"fps": 30, "window_size": [1280, 720], 
            "window_flags": pygame.RESIZABLE | pygame.DOUBLEBUF, 
            "window_bits": 32, "framebuffer_flags": pygame.SRCALPHA, 
            "framebuffer_size": [1280//3, 720//3], "framebuffer_bits": 32,
            "debug": True})

SORA.create_context()

# ------------------------------ #

from scripts.entities import tomato

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
potato = SORA.load_image("assets/sprites/potato-2.png")
__ss = animation.SpriteSheet(SORA.load_image("assets/sprites/stages.png"), 16, 16, 0, 0)

sc = scene.Scene(config=scene.load_config(scene.Scene.DEFAULT_CONFIG))
scw = scene.World(sc.get_config())
scw.get_chunk(0, 0)
sc.add_layer(scw, 0)

# normal entities
sce1 = physics.Entity()
sce2 = physics.Entity()

# particle handlers
sce3particle = physics.ParticleHandler(create_func=physics.ParticleHandler.DEFAULT_CREATE, 
                update_func=physics.ParticleHandler.DEFAULT_UPDATE)
sce3particle.position += (100, 100)

sce4particle = physics.ParticleHandler(create_func="square", update_func="square")
sce4particle.position += (200, 100)
sce4particle["inverval"] = 0.5

sce5particle = physics.ParticleHandler(create_func="triangle", update_func="triangle")
sce5particle.position += (200, 150)
sce5particle["interval"] = 0.4

# collision tests
col1 = physics.Entity()
col2 = physics.Entity()

# ====== add entities to world first
scw.add_entity(sce1)
scw.add_entity(sce2)
# scw.add_entity(sce3particle)
# scw.add_entity(sce4particle)
# scw.add_entity(sce5particle)
scw.add_entity(tomato.Tomato((100, 100)))

scw.add_entity(col1)
scw.add_entity(col2)

# ===== entity comp
sce1.add_component(base_objects.MovementComponent())
sce1.add_component(base_objects.Sprite(0, 0, image))
sce1.add_component(base_objects.SpriteRenderer())
sce1.position += (100, 100)

sce2.add_component(base_objects.MovementComponent())
sce2.add_component(base_objects.AnimatedSprite(0, 0, registry))
sce2.add_component(base_objects.SpriteRenderer())
sce2.position += (200, 100)
sce2.velocity += (30, 10)

# ===== physics
col1.add_component(base_objects.MovementComponent())
col1.add_component(base_objects.Sprite(20, 20, potato))
col1.add_component(base_objects.SpriteRenderer())
col1.add_component(physics.AABB(10, 10))
col1.add_component(base_objects.Collision2DComponent(10, 10))
col1.position += (100, 150)

col2.add_component(base_objects.MovementComponent())
col2.add_component(base_objects.Sprite(20, 20, potato))
col2.add_component(base_objects.SpriteRenderer())
# col2.add_component(physics.Box2D(10, 10, degrees=0))
col2.add_component(physics.AABB(10, 10))
col2.add_component(base_objects.Collision2DComponent(10, 10))
col2.position += (200, 150)

# ===== aspects
scw.add_aspect(base_objects.MovementAspect())
scw.add_aspect(base_objects.Collision2DAspect())
# scw.add_aspect(base_objects.SpriteRendererAspect())
scw.add_aspect(base_objects.SpriteRendererAspectDebug())
scw.add_aspect(base_objects.Collision2DRendererAspectDebug())

scene.SceneHandler.push_scene(sc)


# ------------------------------ #
# game loop
SORA.start_engine_time()
while SORA.RUNNING:
    # SORA.FRAMEBUFFER.fill((255, 255, 255, 255))
    SORA.FRAMEBUFFER.fill((0, 0, 0, 255))
    # pygame update + render
    registry.update()
    scene.SceneHandler.update()
    
    # for i, spr in enumerate(__ss):
    #     pygame.draw.rect(SORA.FRAMEBUFFER, (255, 100, 100), pygame.Rect((i*16 + 200, 30), spr.get_frame().get_size()))
    #     SORA.FRAMEBUFFER.blit(spr.get_frame(), (i*16 + 200, 30))
    # p = [pgmath.Vector2(0, 0), pgmath.Vector2(100, 100), pgmath.Vector2(100, 150)]
    # pgdraw.polygon(SORA.FRAMEBUFFER, (0, 0, 255), p, 1)
    
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

