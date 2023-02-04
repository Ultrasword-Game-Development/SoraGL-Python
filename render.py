import pygame
import soragl
import struct

import numpy as np

from pygame import draw as pgdraw
from pygame import math as pgmath
from soragl import animation, scene, physics, base_objects, sglm

# ------------------------------ #
# setup
SORA = soragl.SoraContext.initialize({
        "fps": 30, 
        "window_size": [1280, 720], 
        "window_flags": pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF, 
        "window_bits": 32, 
        "framebuffer_flags": pygame.SRCALPHA, 
        "framebuffer_size": [1280//3, 720//3], 
        "framebuffer_bits": 32,
        "debug": True,
})

SORA.create_context()

# ------------------------------ #
# import gl?
if SORA.is_flag_active(pygame.OPENGL):
    from soragl import mgl
    from soragl.mgl import ModernGL
    print('Configured Pygame for OpenGL')


# ------------------------------ #
# post setup

ModernGL.create_context(options={
            "standalone": False, 
            "gc_mode": "context_gc", 
            "clear_color": [0.0, 0.0, 0.0, 1.0], 
    })


"""
TODO:
1. load .obj file
2. buffers
3. vao
4. shader
5. camera matrix --> uploading matrices
6. multiple textures handling
7. rendering
"""

camera = base_objects.Camera3D((0, 0, -10), (0, 0, 0), 45/3.14, 16/9)

print(camera.get_view_matrix())
print(camera.get_projection_matrix())

# ------------------------------ #


shader = mgl.ShaderProgram("assets/shaders/default3d.glsl")

# vertex = x, y, z, u, v, r, g, b, a
# 9 items
vertices = mgl.Buffer('36f',  [
        -1.0, -1.0, 0.0,    0.0, 0.0,    1.0, 0.0, 0.0, 1.0,
        1.0, -1.0, 1.0,     1.0, 0.0,    0.0, 1.0, 0.0, 1.0,
        1.0, 1.0, 1.0,      1.0, 1.0,    0.0, 0.0, 1.0, 1.0,
        -1.0, 1.0, 0.0,     0.0, 1.0,    1.0, 1.0, 1.0, 1.0
])

indices = mgl.Buffer('6i', [0, 1, 2, 3, 0, 2])
vattrib = mgl.VAO()
vattrib.add_attribute('3f', 'vvert')
vattrib.add_attribute('2f', 'vuv')
vattrib.add_attribute('4f', 'vcolor')
# add attribs?
vattrib.create_structure(vertices, indices)

# matrix upload
print(vattrib.uniforms)
aa = tuple(shader.program[x] for x in iter(shader.program))
print(aa)
l = aa[-1]
print(l.array_length, l.dimension, l.read())

c = camera.get_view_matrix()
print(c)

cc = np.array([[1, 0, 0, 0]]*4, dtype=np.float32).tobytes()
print(cc)
print(camera.get_view_matrix())

# TODO: check this out please >????/
# this works apparently
shader.program['view'].write(camera.get_view_matrix().tobytes())
shader.program['proj'].write(camera.get_projection_matrix().tobytes())

print(shader.program['proj'].value)

# vattrib.change_uniform_vector("view", camera.get_view_matrix())
# vattrib.change_uniform_vector("view", cc)
# vattrib.change_uniform_vector("proj", camera.get_projection_matrix())

# exit()

# ------------------------------ #
# game loop
SORA.start_engine_time()
while SORA.RUNNING:
    # SORA.FRAMEBUFFER.fill((255, 255, 255, 255))
    # SORA.FRAMEBUFFER.fill((0, 0, 0, 255))
    # SORA.DEBUGBUFFER.fill((0, 0, 0, 0))
    # pygame update + render

    if SORA.is_key_clicked(pygame.K_d) and SORA.is_key_pressed(pygame.K_LSHIFT):
        SORA.DEBUG = not SORA.DEBUG

    # SORA.FRAMEBUFFER.blit(SORA.DEBUGBUFFER, (0, 0))

    # moderngl render
    ModernGL.update_context()
    ModernGL.CTX.clear(ModernGL.CLEARCOLOR[0], ModernGL.CLEARCOLOR[1], ModernGL.CLEARCOLOR[2], ModernGL.CLEARCOLOR[3])
    ModernGL.CTX.enable(mgl.moderngl.BLEND)
    # vattrib.change_uniform("utime", SORA.ENGINE_UPTIME % 10000)
    # vattrib.change_uniform("framebuffer", mgl.Texture.pg2gltex(SORA.FRAMEBUFFER, "fb"))
    # vattrib.change_uniform("debugbuffer", mgl.Texture.pg2gltex(SORA.DEBUGBUFFER, "db"))

    vattrib.render(mode=mgl.moderngl.TRIANGLES)
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

