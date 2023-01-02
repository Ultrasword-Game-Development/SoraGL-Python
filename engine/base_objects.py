import engine
from engine import scene, physics, mgl, animation

import math


# ------------------------------ #
# base physics objects - entity -- components

class MovementComponent(scene.Component):
    def __init__(self, speed: float = 0.0, direction: float = 0.0):
        super().__init__()
        self.speed = speed
        self.direction = direction
        # defined after being added to an entity
        self._entity = None


# ------------------------------ #
# base aspect objects

class MovementAspect(scene.Aspect):
    def __init__(self):
        super().__init__(MovementComponent)
        self.priority = 5
        self.world = None
    
    def handle(self):
        """Handle movement for entities"""
        for e in self.iterate_entities():
            # just move entities first
            comp = e.get_component_from_hash(self._target)
            # handle movement
            e.position.x += comp.speed * math.cos(comp.direction)
            e.position.y += comp.speed * math.sin(comp.direction)

            print(e.position)



