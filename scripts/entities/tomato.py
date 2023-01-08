import pygame
import engine

from engine import animation, physics, scene, misc, base_objects

"""
Tomato - Sprite Testing
"""


# ------------------------------ #
# pre compose

# ------------------------------ #
# class

class Tomato(physics.Entity):
    SPEED = 40
    LERP = 0.3

    def __init__(self, position: tuple):
        super().__init__()
        self.registry = animation.Category.get_category_framedata("assets/sprites/tomato.json")["idle"].get_registry()
        # ------------------------------ #
        self.position += position

    def on_ready(self):
        """
        Called when the entity is added to the world
        """
        self.add_component(base_objects.AnimatedSprite(0, 0, self.registry))
        self.add_component(base_objects.SpriteRenderer())
        self.add_component(base_objects.MovementComponent())
        self.add_component(physics.Box2D(10, 10, degrees=0))
        self.add_component(base_objects.Collision2DComponent(16, 16))

    def update(self):
        """Update the tomato"""
        # pre calc
        self.registry.update()
        self.velocity *= self.LERP

        # input handling
        if engine.SoraContext.is_key_pressed(pygame.K_a):
            self.velocity += physics.LEFT * self.SPEED 
        if engine.SoraContext.is_key_pressed(pygame.K_d):
            self.velocity += physics.RIGHT * self.SPEED
        if engine.SoraContext.is_key_pressed(pygame.K_w):
            self.velocity += physics.UP * self.SPEED
        if engine.SoraContext.is_key_pressed(pygame.K_s):
            self.velocity += physics.DOWN * self.SPEED
        



