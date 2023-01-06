import engine
from engine import scene, physics, mgl, animation

import math

from pygame import math as pgmath

"""
1. sprite / rendering components + rendering aspect
2. collision detection component + collision handling aspect

"""

# ------------------------------------------------------------ #
# errors

class MissingComponent(Exception):
    def __init__(self, *args):
        super().__init__(*args)

# ------------------------------------------------------------ #
# base physics objects - entity -- components
# base aspect objects
# ------------------------------------------------------------ #

# ------------------------------ #
# movement 
class MovementComponent(scene.Component):
    def __init__(self, velocity: float = 0.0, direction: float = 0.0):
        super().__init__()
        self.velocity = velocity
        self.direction = direction
        # print("in movement class")
        # print(self.__class__.__name__)
        # print(hash(self))

# aspect
class MovementAspect(scene.Aspect):
    def __init__(self):
        super().__init__(MovementComponent, 5)
        self.priority = 5
        # print("created movement aspect", self.priority)
    
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


# ------------------------------ #
# sprite
# NOTE: sprite / animated sprite must be added before renderer!

# exception
class MissingSprite(Exception):
    def __init__(self, *args):
        super().__init__(*args)

# sprite
class Sprite(scene.Component):
    def __init__(self, width: int, height: int, sprite = None):
        super().__init__()
        self.width = width
        self.height = height
        if width < 0 or height < 0:
            raise ValueError("Width and height must be greater than 0!")
        elif width == 0 or height == 0:
            self._sprite = sprite
            self.width, self.height = self._sprite.get_size()
        else:
            self._sprite = engine.SoraContext.scale_image(sprite, (width, height)) if sprite else sprite
        self.hwidth = self.width // 2
        self.hheight = self.height // 2

    @property
    def sprite(self):
        """Get the sprite"""
        return self._sprite
    
    @sprite.setter
    def sprite(self, new):
        """Set a new sprite"""
        self._sprite = engine.SoraContext.scale_image(new, (self.width, self.height))
    
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
        self.sprite = engine.SoraContext.scale_image(self.sprite, (self.width, self.height))

# animated sprite
class AnimatedSprite(Sprite):
    def __init__(self, width: int, height: int, registry):
        super().__init__(width, height, registry.get_frame())
        self._registry = registry
    
    @property
    def sprite(self):
        """Get the sprite"""
        return self._registry.get_frame()

    @property
    def area(self):
        """Get the area"""
        return self._registry.get_frame().get_size()

# renderer
class SpriteRenderer(scene.Component):
    def __init__(self):
        super().__init__()
        self._sprite = None

    def on_add(self):
        """On add"""
        # check if parent entity has a sprite component
        # if not self._entity.entity_has_component(Sprite):
        #     raise MissingSprite("Sprite is not an added component")
        self._sprite = self._entity.get_component(Sprite)
        if not self._sprite:
            self._sprite = self._entity.get_component(AnimatedSprite)

# aspect
class SpriteRendererAspect(scene.Aspect):
    def __init__(self):
        super().__init__(SpriteRenderer)
        self.priority = 0
    
    def handle(self):
        """Render the sprites"""
        for e in self.iterate_entities():
            # get the sprite
            c_sprite = e.get_component(SpriteRenderer)._sprite
            if not c_sprite.sprite: continue
            # get the position
            pos = e.position.xy
            # render the sprite
            engine.SoraContext.FRAMEBUFFER.blit(c_sprite.sprite, pos - (c_sprite.hwidth, c_sprite.hheight))

# ------------------------------ #
# collision2d
class Collision2DComponent(scene.Component):
    # square
    DEFAULT = {"mass": 10}

    def __init__(self, width: int, height: int, angle: float = 0, mass: float = 10, hardness: float = 1.0, offset: list = None):
        super().__init__()
        self.width = width
        self.height = height
        self.angle = angle
        self._offset = pgmath.Vector2(offset) if offset else pgmath.Vector2(0, 0)
        # other arguments
        self._mass = mass
        self._area = self.width * self.height
        self._density = self._area / self._mass
        self._hardness = hardness

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

    def get_relative_position(self):
        """Get the relative position"""
        return self._offset + self._entity.position

    def get_offset(self):
        """Get the offset"""
        return self._offset

    def is_collided(self, other):
        """Check if this entity is collided with another entity"""
        # get the position
        pos = self.get_relative_position()
        other_pos = other.get_relative_position()
        # using SAT for AABB collision
        

# https://github.com/codingminecraft/MarioYoutube/blob/265780291acc7693816ff2723c227ae89a171466/src/main/java/physics2d/rigidbody/IntersectionDetector2D.java



# aspect
class Collision2DAspect(scene.Aspect):
    def __init__(self):
        super().__init__(Collision2DComponent)
        self.priority = 10
        # private
        self._collisions = []
    
    def has_collision(self, e1, e2):
        """Check if there are collisions"""
        pass

    def handle(self):
        """Handle Collisions for Collision2D Components"""
        # consider chunking
        
        pass

# ------------------------------ #
# handling collision

class Collision2DHandler:
    def __init__(self):
        super().__init__(0)
        self._collision2d_aspect = None
    
    def on_add(self):
        """On add"""
        self._collision2d_aspect = self._world.get_aspect(Collision2DAspect)
        if not self._collision2d_aspect:
            raise MissingComponent("Collision2DAspect is not an added component")
    
    def handle(self):
        # perform collisions!
        pass






print("More objects to be added! base_objects.py")
