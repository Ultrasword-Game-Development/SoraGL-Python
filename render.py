import pygame
import soragl
import struct
import glm

import numpy as np

from pygame import draw as pgdraw
from pygame import math as pgmath
from soragl import animation, scene, physics, base_objects, misc

# ------------------------------ #
# setup
SORA = soragl.SoraContext.initialize(
    {
        "fps": 30,
        "window_size": [1280, 720],
        "window_flags": pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF,
        "window_bits": 32,
        "framebuffer_flags": pygame.SRCALPHA,
        "framebuffer_size": [1280 // 3, 720 // 3],
        "framebuffer_bits": 32,
        "debug": True,
    }
)

SORA.create_context()
# ------------------------------ #
# import gl?
if SORA.is_flag_active(pygame.OPENGL):
    from soragl import mgl
    from soragl.mgl import ModernGL

    print("Configured Pygame for OpenGL")

# ------------------------------ #
# post setup

ModernGL.create_context(
    options={
        "standalone": False,
        "gc_mode": "context_gc",
        "clear_color": [0.0, 0.0, 0.0, 1.0],
        "depth_test": True,
    }
)


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

# ------------------------------ #

# no need to manulaly create a shader program
# shader = mgl.ShaderProgram("assets/shaders/default.glsl")
# shader = mgl.ShaderProgram("assets/shaders/3testing.glsl")

# box
box = mgl.Buffer(
    "40f",
    [
        # order: front
        # bot left, clockwise
        -0.5,
        -0.5,
        -0.5,
        0.0,
        0.0,
        0.5,
        -0.5,
        -0.5,
        1.0,
        0.0,
        0.5,
        0.5,
        -0.5,
        1.0,
        1.0,
        -0.5,
        0.5,
        -0.5,
        0.0,
        1.0,
        # back
        # bot left, ccw
        -0.5,
        -0.5,
        0.5,
        0.0,
        0.0,
        0.5,
        -0.5,
        0.5,
        1.0,
        0.0,
        0.5,
        0.5,
        0.5,
        1.0,
        1.0,
        -0.5,
        0.5,
        0.5,
        0.0,
        1.0,
    ],
)
bind = mgl.Buffer(
    "36i",
    [
        # front face
        0,
        1,
        2,
        3,
        0,
        2,
        # right face
        1,
        5,
        6,
        2,
        1,
        6,
        # back face
        5,
        4,
        7,
        6,
        5,
        7,
        # left face
        4,
        0,
        3,
        7,
        4,
        3,
        # top face
        3,
        2,
        6,
        7,
        3,
        6,
        # bottom face
        4,
        5,
        1,
        0,
        4,
        1,
    ],
)

cubes = [
    glm.vec3(0, 2, 0),
    glm.vec3(0, 0, 1),
    glm.vec3(2, 0, 2),
    glm.vec3(-2, -1, 3),
    glm.vec3(-0.23, 2, 4),
]

scales = [
    glm.vec3(1, 1, 1),
    glm.vec3(1, 1, 1),
    glm.vec3(1, 1, 1),
    glm.vec3(1, 1, 1),
    glm.vec3(2, 2, 2),
]

battrib = mgl.VAO("assets/shaders/3testing.glsl")
battrib.add_attribute("3f", "vvert")
battrib.add_attribute("2f", "vuv")
# create
battrib.create_structure(box, bind)


# vertex = x, y, z, u, v, r, g, b, a
# 9 items
vertices = mgl.Buffer(
    "36f",
    [
        # bottom left, ccw
        -1.0,
        -1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        -1.0,
        0.0,
        1.0,
        0.0,
        0.0,
        1.0,
        0.0,
        1.0,
        1.0,
        1.0,
        0.0,
        1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        -1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ],
)

indices = mgl.Buffer("6i", [0, 1, 2, 3, 0, 2])
vattrib = mgl.VAO("assets/shaders/default3d.glsl")
vattrib.add_attribute("3f", "vvert")
vattrib.add_attribute("2f", "vuv")
vattrib.add_attribute("4f", "vcolor")
# add attribs?
vattrib.create_structure(vertices, indices)

# camera
camera = base_objects.FrustCamera((0, 0, -10), (0, 0, -1), 60, 16 / 9)
camera.set_rotation(270, -180, 0)
SPEED = 10

vattrib.change_uniform_vector("view", camera.get_view_matrix())
vattrib.change_uniform_vector("proj", camera.get_projection_matrix())
battrib.change_uniform_vector("view", camera.get_view_matrix())
battrib.change_uniform_vector("proj", camera.get_projection_matrix())

# exit()

MLOCK = misc.MouseLocking(0.5, 0.5)

# ------------------------------ #
# game loop
ModernGL.set_clear_color([1.0, 1.0, 1.0, 1.0])
SORA.start_engine_time()
while SORA.RUNNING:
    # pygame update + render
    if SORA.is_key_clicked(pygame.K_d) and SORA.is_key_pressed(pygame.K_LSHIFT):
        SORA.DEBUG = not SORA.DEBUG

    # testing
    if SORA.is_key_pressed(pygame.K_d):
        camera.r_translate(SPEED * SORA.DELTA, 0, 0)
    if SORA.is_key_pressed(pygame.K_a):
        camera.r_translate(-SPEED * SORA.DELTA, 0, 0)
    if SORA.is_key_pressed(pygame.K_w):
        camera.r_translate(0, 0, SPEED * SORA.DELTA)
    if SORA.is_key_pressed(pygame.K_s):
        camera.r_translate(0, 0, -SPEED * SORA.DELTA)

    if SORA.is_key_clicked(pygame.K_ESCAPE):
        MLOCK.locked = not MLOCK.locked
        MLOCK.hidden = not MLOCK.hidden

    MLOCK.update()
    # calculate rotation
    camera.rotate(MLOCK.delta[0] * 300, -MLOCK.delta[1] * 300, 0)
    # mouse movement for rotation
    print(camera.position, camera.rotation, camera.target)

    vattrib.change_uniform_vector("view", camera.get_view_matrix())
    battrib.change_uniform_vector("view", camera.get_view_matrix())

    # moderngl render
    ModernGL.CTX.screen.use()
    ModernGL.update_context()
    ModernGL.CTX.clear(
        ModernGL.CLEARCOLOR[0],
        ModernGL.CLEARCOLOR[1],
        ModernGL.CLEARCOLOR[2],
        ModernGL.CLEARCOLOR[3],
    )
    ModernGL.CTX.enable(mgl.moderngl.BLEND)

    vattrib.render(mode=mgl.moderngl.TRIANGLES)
    for i, cube in enumerate(cubes):
        model = glm.mat4(1)
        model = glm.translate(model, cube)
        angle = 20.0 * i
        model = glm.rotate(model, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))

        battrib.change_uniform_vector("model", model)
        # battrib.change_uniform_vector("scale", scales[i])
        battrib.render(mode=mgl.moderngl.TRIANGLES)
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
