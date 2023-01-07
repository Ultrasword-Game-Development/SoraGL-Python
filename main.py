import pygame
import engine
import struct

from pygame import draw as pgdraw
from pygame import math as pgmath
from engine import animation, scene, physics, base_objects

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
    from engine import mgl
    from engine.mgl import ModernGL
    print('Configured Pygame for OpenGL')


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


"""
TODO:
4. cleaning up buffers --> releasing all gl context data

ERRORS:
1. resizing window increases RAM usage -- maybe opengl error? gc?
"""


animation.Category.load_category("assets/sprites/tomato.json")
registry = animation.Category.get_category_framedata("assets/sprites/tomato.json")["idle"].get_registry()


image = SORA.load_image("assets/sprites/tomato.png")
__ss = animation.SpriteSheet(SORA.load_image("assets/sprites/stages.png"), 16, 16, 0, 0)

sc = scene.Scene(config=scene.load_config(scene.Scene.DEFAULT_CONFIG))
scw = scene.World(sc.get_config())
scw.get_chunk(0, 0)
sc.add_layer(scw, 0)

sce1 = physics.Entity()

sce2 = physics.Entity()

sce3particle = physics.ParticleHandler(create_func=physics.ParticleHandler.DEFAULT_CREATE, 
                update_func=physics.ParticleHandler.DEFAULT_UPDATE)
sce3particle.position += (100, 100)

sce4particle = physics.ParticleHandler(create_func="square", update_func="square")
sce4particle.position += (200, 100)
sce4particle["inverval"] = 0.5

sce5particle = physics.ParticleHandler(create_func="triangle", update_func="triangle")
sce5particle.position += (200, 150)
sce5particle["interval"] = 0.4

# add entities to world first
scw.add_entity(sce1)
scw.add_entity(sce2)
scw.add_entity(sce3particle)
scw.add_entity(sce4particle)
scw.add_entity(sce5particle)


# entity comp
sce1.add_component(base_objects.MovementComponent())
sce1.add_component(base_objects.Sprite(0, 0, image))
sce1.add_component(base_objects.SpriteRenderer())
sce1.position += (100, 100)

sce2.add_component(base_objects.MovementComponent(2, 0.1))
sce2.add_component(base_objects.AnimatedSprite(0, 0, registry))
sce2.add_component(base_objects.SpriteRenderer())


# physics
sce1.add_component(physics.AABB(10, 10))
sce1.add_component(base_objects.Collision2DComponent(10, 10))

sce2.add_component(physics.Box2D(10, 10, degrees=0))
sce2.add_component(base_objects.Collision2DComponent(10, 10))


# aspects
scw.add_aspect(base_objects.MovementAspect())
scw.add_aspect(base_objects.Collision2DAspect())
# scw.add_aspect(base_objects.SpriteRendererAspect())
scw.add_aspect(base_objects.SpriteRendererAspectDebug())

scene.SceneHandler.push_scene(sc)


# ------------------------------ #
# game loop
SORA.start_engine_time()
while SORA.RUNNING:
    SORA.FRAMEBUFFER.fill((255, 255, 255, 255))
    # pygame update + render
    scene.SceneHandler.update()


    # registry.update()
    # pygame.draw.rect(SORA.FRAMEBUFFER, (0, 0, 255), pygame.Rect((200, 120), registry.get_frame().get_size()))
    # SORA.FRAMEBUFFER.blit(registry.get_frame(), (200, 120))

    # for i, spr in enumerate(__ss):
    #     pygame.draw.rect(SORA.FRAMEBUFFER, (255, 100, 100), pygame.Rect((i*16 + 200, 30), spr.get_frame().get_size()))
    #     SORA.FRAMEBUFFER.blit(spr.get_frame(), (i*16 + 200, 30))

    # moderngl render
    ModernGL.update_context()
    ModernGL.CTX.clear(ModernGL.CLEARCOLOR[0], ModernGL.CLEARCOLOR[1], ModernGL.CLEARCOLOR[2], ModernGL.CLEARCOLOR[3])
    ModernGL.CTX.enable(mgl.moderngl.BLEND)
    vattrib.change_uniform("utime", SORA.ENGINE_UPTIME % 10000)
    vattrib.change_uniform("framebuffer", mgl.Texture.pg2gltex(SORA.FRAMEBUFFER, "fb"))

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

