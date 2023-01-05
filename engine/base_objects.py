import engine
from engine import scene, physics, mgl, animation

import math

"""
1. sprite / rendering components + rendering aspect
2. collision detection component + collision handling aspect

"""

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
# collision2d
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

# aspect
class Collision2DAspect(scene.Aspect):
    def __init__(self):
        super().__init__(Collision2DComponent)
        self.priority = 10
    
    def handle(self):
        """Handle Collisions for Collision2D Components"""
        # consider chunking
        pass

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

print("More objects to be added! base_objects.py")
