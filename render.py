import pygame
import soragl
import struct
import glm

import numpy as np

from pygame import draw as pgdraw
from pygame import math as pgmath
from soragl import animation, scene, physics, base_objects, misc, smath

from soragl._3d import model

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
        #
        0.5,
        -0.5,
        -0.5,
        1.0,
        0.0,
        #
        0.5,
        0.5,
        -0.5,
        1.0,
        1.0,
        #
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
        #
        0.5,
        -0.5,
        0.5,
        1.0,
        0.0,
        #
        0.5,
        0.5,
        0.5,
        1.0,
        1.0,
        #
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
cubes = [glm.vec3(np.random.uniform(-10, 10, 3)) for _ in range(10)]

# TODO: later
scales = [
    glm.mat4([x, 0, 0, 0], [0, x, 0, 0], [0, 0, x, 0], [0, 0, 0, 1])
    for x in np.linspace(1, 4, 10)
]

# ------------------------------ #

battrib = mgl.VAO("assets/shaders/3testing.glsl")
battrib.add_attribute("3f", "vvert")
battrib.add_attribute("2f", "vuv")
# create
battrib.create_structure(box, bind)

# vertex = x, y, z, u, v, r, g, b, a, texnum
# 10 items
vertices = mgl.Buffer(
    "80f",
    [
        # bottom left, ccw
        -1.0,
        -1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        0.0,
        # bottom right
        1.0,
        -1.0,
        0.0,
        1.0,
        1.0,
        0.0,
        1.0,
        0.0,
        1.0,
        0.0,
        # top right
        1.0,
        1.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        1.0,
        0.0,
        # top left
        -1.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        1.0,
        0.0,
        #
        #
        # second
        # bottom left, ccw
        -3.0,
        -3.0,
        1.0,
        0.0,
        1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        # bottom right
        -1.0,
        -3.0,
        1.0,
        1.0,
        1.0,
        0.0,
        1.0,
        0.0,
        1.0,
        1.0,
        # top right
        -1.0,
        -1.0,
        1.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        1.0,
        1.0,
        # top left
        -3.0,
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

indices = mgl.Buffer("12i", [0, 1, 2, 3, 0, 2, 4, 5, 6, 7, 4, 6])
vattrib = mgl.VAO("assets/shaders/default3d.glsl")
vattrib.add_attribute("3f", "vvert")
vattrib.add_attribute("2f", "vuv")
vattrib.add_attribute("4f", "vcolor")
vattrib.add_attribute("1f", "vtex")
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

# ------------------------------ #
# textures

thandler = mgl.TextureHandler()
thandler.load_texture("assets/sprites/tomato-1.png")
thandler.load_texture("assets/sprites/tomato-2.png")
thandler.bind_textures(vattrib, "uarray")

# ------------------------------ #
# loading models

tmodel = model.MTLObjLoader("assets/models/model")
tmodel.load()

sample = tmodel.get_object("cube")
samplehandler = mgl.VAO("assets/shaders/model.glsl")
samplehandler.add_attribute("3f", "vvert")
samplehandler.add_attribute("2f", "vuv")
samplehandler.add_attribute("3f", "vnorm")
samplehandler.create_structure(sample._vbuffer)

# default uniforms
model = glm.mat4(1)
model = glm.translate(model, glm.vec3(1, 0, 0))
model = glm.rotate(model, glm.radians(20.0), glm.vec3(1.0, 0.3, 0.5))
samplehandler.change_uniform_vector("model", model)

scale = glm.mat4(1)
scale = glm.scale(scale, glm.vec3(5, 5, 5))
samplehandler.change_uniform_vector("scale", scale)

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
    if SORA.is_key_pressed(pygame.K_SPACE):
        camera.r_translate(0, SPEED * SORA.DELTA, 0)
    if SORA.is_key_pressed(pygame.K_LSHIFT):
        camera.r_translate(0, -SPEED * SORA.DELTA, 0)
    if SORA.is_key_clicked(pygame.K_ESCAPE):
        MLOCK.locked = not MLOCK.locked
        MLOCK.hidden = not MLOCK.hidden
    MLOCK.update()
    # calculate rotation
    camera.rotate(MLOCK.delta[0] * 300, -MLOCK.delta[1] * 300, 0)
    camera.pitch = smath.__clamp__(camera.pitch, -89.0, 89.0)
    # ------------------------------ #
    # render
    # moderngl context update
    ModernGL.CTX.screen.use()
    ModernGL.update_context()
    ModernGL.CTX.clear(
        ModernGL.CLEARCOLOR[0],
        ModernGL.CLEARCOLOR[1],
        ModernGL.CLEARCOLOR[2],
        ModernGL.CLEARCOLOR[3],
    )
    ModernGL.CTX.enable(mgl.moderngl.BLEND)

    # now to render the model
    # print(samplehandler.uniforms)

    sample._texture.use(1)
    samplehandler.change_uniform_scalar("tex", 1)
    samplehandler.change_uniform_vector("view", camera.get_view_matrix())
    samplehandler.change_uniform_vector("proj", camera.get_projection_matrix())
    samplehandler.render(mode=mgl.moderngl.TRIANGLES)

    thandler.bind_textures(vattrib, "uarray")
    # rendering
    vattrib.change_uniform_vector("view", camera.get_view_matrix())
    battrib.change_uniform_vector("view", camera.get_view_matrix())

    vattrib.render(mode=mgl.moderngl.TRIANGLES)
    for i, cube in enumerate(cubes):
        model = glm.mat4(1)
        model = glm.translate(model, cube)
        angle = 20.0 * i
        model = glm.rotate(model, glm.radians(angle), glm.vec3(1.0, 0.3, 0.5))

        battrib.change_uniform_vector("model", model)
        battrib.change_uniform_vector("scale", scales[i])
        battrib.render(mode=mgl.moderngl.TRIANGLES)
    ModernGL.CTX.disable(mgl.moderngl.BLEND)

    thandler.unbind_textures()

    # ------------------------------ #

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
