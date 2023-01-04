import engine
from engine import scene, physics, mgl, animation

import math

"""
1. sprite / rendering components + rendering aspect
2. collision detection component + collision handling aspect

"""

# ------------------------------ #
# base physics objects - entity -- components
# base aspect objects


# movement

class MovementComponent(scene.Component):
    def __init__(self, velocity: float = 0.0, direction: float = 0.0):
        super().__init__()
        self.velocity = velocity
        self.direction = direction
        # print("in movement class")
        # print(self.__class__.__name__)
        # print(hash(self))


class MovementAspect(scene.Aspect):
    def __init__(self):
        super().__init__(MovementComponent, 5)
        self.priority = 5
        print("created movement aspect", self.priority)
    
    def handle(self):
        """Handle movement for entities"""
        for e in self.iterate_entities():
            # just move entities first
            comp = e.get_component_from_hash(self._target)
            # handle movement
            e.position.x += comp.velocity * math.cos(comp.direction)
            e.position.y += comp.velocity * math.sin(comp.direction)
            # push object towards position
            e.rect.center = e.position.xy
            # print(e.rect)

# collision

class Collision2DComponent(scene.Component):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.width = width
        self.height = height

    @property
    def area(self):
        """Get the area"""
        return (self.width, self.height)
    
    @area.setter
    def area(self, new_area: tuple):
        """set a new area"""
        if len(new_area) != 2:
            raise NotImplementedError(f"The area {new_area} is not supported yet! {__file__} {__package__}")
        self.width, self.height = new_area


class Collision2DAspect(scene.Aspect):
    def __init__(self):
        super().__init__(Collision2DComponent)
        self.priority = 10
    
    def handle(self):
        """Handle Collisions for Collision2D Components"""
        # consider chunking
        pass


# sprite rendering

# NOTE: must add sprite comp before sprite renderer component!

