import pygame
import soragl

from soragl import animation, physics, scene, misc, base_objects

"""
Tomato - Sprite Testing
"""


# ------------------------------ #
# pre compose

# ------------------------------ #
# class

class Tomato(physics.Entity):
    SPEED = 50
    LERP = 0.3

    def __init__(self, position: tuple):
        super().__init__()
        self.registry = animation.Category.get_category_framedata("assets/sprites/tomato.json")["idle"].get_registry()
        # ------------------------------ #
        self.position += position
        self.area = (16, 16)

    def on_ready(self):
        """
        Called when the entity is added to the world
        """
        self.add_component(base_objects.AnimatedSprite(0, 0, self.registry))
        self.add_component(base_objects.SpriteRenderer())
        self.add_component(base_objects.Collision2DComponent())

    def update(self):
        """Update the tomato"""
        # pre calc
        self.registry.update()
        self.velocity *= self.LERP

        # input handling
        if soragl.SoraContext.is_key_pressed(pygame.K_a):
            self.velocity += physics.World2D.LEFT * self.SPEED 
        if soragl.SoraContext.is_key_pressed(pygame.K_d):
            self.velocity += physics.World2D.RIGHT * self.SPEED
        if soragl.SoraContext.is_key_pressed(pygame.K_w):
            self.velocity += physics.World2D.UP * self.SPEED
        if soragl.SoraContext.is_key_pressed(pygame.K_s):
            self.velocity += physics.World2D.DOWN * self.SPEED
        



