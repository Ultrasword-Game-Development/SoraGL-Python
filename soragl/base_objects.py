import soragl
from soragl import scene, physics, mgl, animation

import random
import math

from pygame import Rect as pgRect
from pygame import math as pgmath
from pygame import draw as pgdraw

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
    def __init__(self):
        super().__init__()

# aspect
class MovementAspect(scene.Aspect):
    def __init__(self):
        super().__init__(MovementComponent, 20)
        self.priority = 5
        # print("created movement aspect", self.priority)
    
    def handle(self):
        """Handle movement for entities"""
        for e in self.iterate_entities():
            # just move entities first
            # comp = e.get_component_from_hash(self._target)
            # handle movement
            e.position += e.velocity * soragl.SoraContext.DELTA
            # push object towards position
            e.rect.center = e.position.xy

            # if e.__class__.__name__ == "Tomato":
            #     print(e.velocity)

            # handle if leaving chunk
            cx = e.rect.centerx // e.world._options["chunkpixw"]
            cy = e.rect.centery // e.world._options["chunkpixh"]
            if cx != e.c_chunk[0] or cy != e.c_chunk[1]:
                # update chunk data
                self._world.update_entity_chunk(e, e.c_chunk, (cx, cy))


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
            raise ValueError("Width and height must be >= 0!")
        elif width == 0 or height == 0:
            self._sprite = sprite
            self.width, self.height = self._sprite.get_size()
        else:
            self._sprite = soragl.SoraContext.scale_image(sprite, (width, height)) if sprite else sprite
        self.hwidth = self.width // 2
        self.hheight = self.height // 2
        # print(self.width, self.height, self._sprite)

    @property
    def sprite(self):
        """Get the sprite"""
        return self._sprite
    
    @sprite.setter
    def sprite(self, new):
        """Set a new sprite"""
        self._sprite = soragl.SoraContext.scale_image(new, (self.width, self.height))
    
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
        self.sprite = soragl.SoraContext.scale_image(self.sprite, (self.width, self.height))

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
    def registry(self):
        """Get the registry"""
        return self._registry
    
    @registry.setter
    def registry(self, new):
        """Set a new registry"""
        self._registry = new

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
        # print(self._sprite)

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
            soragl.SoraContext.FRAMEBUFFER.blit(c_sprite.sprite, pos - (c_sprite.hwidth, c_sprite.hheight))

# debug aspect
class SpriteRendererAspectDebug(scene.Aspect):
    def __init__(self):
        super().__init__(SpriteRenderer)
        self.priority = 0
    
    def handle(self):
        """Render the sprites"""
        for e in self.iterate_entities():
            # get the sprite
            c_sprite = e.get_component(SpriteRenderer)._sprite
            # print(c_sprite)
            if not c_sprite or not c_sprite.sprite: continue
            # print(c_sprite)
            # render the sprite
            soragl.SoraContext.FRAMEBUFFER.blit(c_sprite.sprite, e.position - (c_sprite.hwidth, c_sprite.hheight))
            pgdraw.rect(soragl.SoraContext.DEBUGBUFFER, (0, 0, 255), pgRect(e.position - (c_sprite.hwidth, c_sprite.hheight), c_sprite.sprite.get_size()), 1)


# ------------------------------ #
# collision2d
class Collision2DComponent(scene.Component):
    # square
    DEFAULT = {
        "mass": 1, 
        "hardness": 1.0, # hardness
    }

    TARGETS = [physics.AABB, physics.Box2D]

    def __init__(self, mass: float = 1, hardness: float = 1.0, offset: list = None):
        super().__init__()
        # private
        self._offset = pgmath.Vector2(offset) if offset else pgmath.Vector2(0, 0)
        # other arguments
        self._mass = mass
        self._area = 0
        self._density = 0
        self._hardness = hardness
        self._shape = None
        # public 
        self._force = pgmath.Vector2()

    def on_add(self):
        """On add"""
        for t in Collision2DComponent.TARGETS:
            if self._entity.entity_has_component(t):
                self._shape = self._entity.get_component(t)
                break
        if not self._shape:
            raise MissingShape("Shape is not an added component to: ", self._entity)
        # print(self._shape)
        self._area = self._shape._rect.w * self._shape._rect.h
        self._density = self._area / self._mass

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

    @property
    def force(self):
        """Get the force"""
        return self._force

    def apply_force(self, force: pgmath.Vector2):
        """Apply a force to the component"""
        self._force += force

# aspect
class Collision2DAspect(scene.Aspect):

    def __init__(self):
        super().__init__(Collision2DComponent)
        self.priority = 19
        # private
        self._collisions = []
        self._cache = set()
        self._handler_aspect = None # to be set after in 'on_add' of the collision2dhandleraspect

    def handle_collision_check(self, a, b) -> bool:
        """Check if there are collisions"""
        # grab the collision components
        ac = a.get_component(Collision2DComponent)
        bc = b.get_component(Collision2DComponent)
        acol = ac._shape
        bcol = bc._shape
        # check if there is a collision along x and y axis
        return physics.check_overlap(acol, bcol, physics.RIGHT) and physics.check_overlap(acol, bcol, physics.UP)
        
    def resolve_collisions(self):
        """Handle the collision

        Find a = axis of collision
        - then using momentum equation:
        - since momentum conserved in 'a'
        - then solve for resulting velocities! in the other axis! (b = perp to a)
        
        find the right function to handle collision :D
        """
        for col in self._collisions:
            # check if the collision is already in the cache
            if col in self._cache: continue
            # add the collision to the cache
            self._cache.add(col)
            # call resolve collision
            physics.resolve_collision(col)

    def update_projected_position(self):
        """Update the projected position of the entities"""
        # update all entity positions first
        for e in self.iterate_entities():
            e._projected_position = e.position + e.velocity

    def find_projected_collisions(self):
        """Find the projected collisions"""
        for e1 in self.iterate_entities():
            for e2 in self.iterate_entities():
                if e1 == e2: continue
                # handle collision checking
                if self.handle_collision_check(e1, e2):
                    physics.resolve_collision(physics.Collision(e1, e2))

    def update_final_positions(self):
        """Update the final positions of the entities"""
        for e in self.iterate_entities():
            e.position = e._projected_position

    def handle(self):
        """Handle Collisions for Collision2D Components"""
        # update projected positions
        self.update_projected_position()
        # find collisions of projected entities
        self.find_projected_collisions()
        # update final positions
        self.update_final_positions()
        # clear cache
        self._collisions.clear()
        self._cache.clear()


# ------------------------------ #
# debug render collision areas

class Collision2DRendererAspectDebug(Collision2DAspect):
    def __init__(self):
        super().__init__()

    def find_projected_collisions(self):
        """Find the projected collisions"""
        for e1 in self.iterate_entities():
            # debug comps
            c1 = e1.get_component(Collision2DComponent)
            pos = c1.get_relative_position()
            # draw collision area
            pgdraw.rect(soragl.SoraContext.FRAMEBUFFER, (255, 0, 0), pgRect(pos - (c1._shape._rect.w/2, c1._shape._rect.h/2), (c1._shape._rect.w, c1._shape._rect.h)), 1)
            # loop entitites
            for e2 in self.iterate_entities():
                if e1 == e2: continue
                # handle collision checking
                self.handle_collision_check(e1, e2)
                
                c2 = e2.get_component(Collision2DComponent)
                # draw a line between the two entities
                center = (e1.position + e2.position) / 2
                if not e1.position - e2.position: continue
                dvec = (e1.position - e2.position).normalize()
                rdvec = dvec.rotate(90)
                pgdraw.line(soragl.SoraContext.DEBUGBUFFER, (0, 255, 0), 
                            center + rdvec * 10, center - rdvec * 10, 1)
                # some more art for support calculations
                rxpos = max(e1.position.x, e2.position.x)
                rypos = max(e1.position.y, e2.position.y)
                # 2 lines for x and y axis
                pgdraw.line(soragl.SoraContext.DEBUGBUFFER, (0, 255, 0),
                            (rxpos, e1.position.y), (rxpos, e2.position.y), 1)
                pgdraw.line(soragl.SoraContext.DEBUGBUFFER, (0, 255, 0),
                            (e1.position.x, rypos), (e2.position.x, rypos), 1)
                # draw support lines
                e1s, e1is = c1._shape.get_support(dvec), c1._shape.get_isupport(dvec)
                e2s, e2is = c2._shape.get_support(dvec), c2._shape.get_isupport(dvec)
                pgdraw.line(soragl.SoraContext.DEBUGBUFFER, (0, 100, 100),
                            e1s, (e1s.x, rypos), 1)
                pgdraw.line(soragl.SoraContext.DEBUGBUFFER, (0, 100, 100),
                            e2s, (e2s.x, rypos), 1)
                pgdraw.line(soragl.SoraContext.DEBUGBUFFER, (0, 100, 100),
                            e1s, (rxpos, e1s.y), 1)
                pgdraw.line(soragl.SoraContext.DEBUGBUFFER, (0, 100, 100),
                            e2s, (rxpos, e2s.y), 1)


# ------------------------------------------------------------ #
# particle system
# ------------------------------------------------------------ #

# ------------------------------ #
# square particle

def create_square_particle(parent, **kwargs):
    """Create a square particle"""
    r = kwargs["radius"] if "radius" in kwargs else 10
    return [parent.position.xy, 
            kwargs["vel"] if "vel" in kwargs else pgmath.Vector2((random.random()-0.5)*100, (random.random()-0.5)*100),
            0, # angle,
            kwargs["angv"] if "angv" in kwargs else (random.random()-0.5) * 100,
            list(kwargs["color"]) if "color" in kwargs else [0, 0, 255],
            kwargs["life"] if "life" in kwargs else 1.0,
            (physics.RIGHT * r, physics.UP * r, physics.LEFT * r, physics.DOWN * r), # points
            parent.get_new_particle_id()]

def update_square_particle(parent, particle):
    """Update a square particle"""
    # check if the particle is dead
    particle[5] -= soragl.SoraContext.DELTA
    # print(particle)
    if particle[5] <= 0:
        parent.remove_particle(particle)
        return
    # set color value
    particle[4][0] = int(math.sin(soragl.SoraContext.ENGINE_UPTIME) * 127 + 127)
    particle[4][1] = int(math.cos(soragl.SoraContext.ENGINE_UPTIME) * 127 + 127)
    particle[4][2] = int(math.sin(particle[0].x) * 127 + 127)
    # just spin + move in random direction
    particle[0] += particle[1] * soragl.SoraContext.DELTA
    particle[2] += particle[3] * soragl.SoraContext.DELTA
    # render -- square (that rotates)
    points = [i.rotate(particle[2]) + particle[0] for i in particle[6]]
    pgdraw.polygon(soragl.SoraContext.FRAMEBUFFER, particle[4], points, 1)


# register
physics.ParticleHandler.register_create_function("square", create_square_particle)
physics.ParticleHandler.register_update_function("square", update_square_particle)

# ------------------------------ #
# triangle particles

def create_triangle_particle(parent, **kwargs):
    """Create a square particle"""
    r = kwargs["radius"] if "radius" in kwargs else 10
    return [parent.position.xy, 
            kwargs["vel"] if "vel" in kwargs else pgmath.Vector2((random.random()-0.5)*100, (random.random()-0.5)*100),
            0, # angle,
            kwargs["angv"] if "angv" in kwargs else (random.random()-0.5) * 1000,
            list(kwargs["color"]) if "color" in kwargs else [0, 0, 255],
            kwargs["life"] if "life" in kwargs else 1.0,
            (physics.RIGHT * r, physics.RIGHT.rotate(120) * r, physics.RIGHT.rotate(240) * r), # points
            parent.get_new_particle_id()]

def update_triangle_particle(parent, particle):
    """Update a square particle"""
    # check if the particle is dead
    particle[5] -= soragl.SoraContext.DELTA
    # print(particle)
    if particle[5] <= 0:
        parent.remove_particle(particle)
        return
    # set color value
    particle[4][0] = int(math.sin(soragl.SoraContext.ENGINE_UPTIME) * 127 + 127)
    particle[4][1] = int(math.cos(soragl.SoraContext.ENGINE_UPTIME) * 127 + 127)
    particle[4][2] = int(math.sin(particle[0].x) * 127 + 127)
    # just spin + move in random direction
    particle[0] += particle[1] * soragl.SoraContext.DELTA
    particle[2] += particle[3] * soragl.SoraContext.DELTA
    # render -- square (that rotates)
    points = [i.rotate(particle[2]) + particle[0] for i in particle[6]]
    pgdraw.polygon(soragl.SoraContext.FRAMEBUFFER, particle[4], points, 1)


# register
physics.ParticleHandler.register_create_function("triangle", create_triangle_particle)
physics.ParticleHandler.register_update_function("triangle", update_triangle_particle)

# ------------------------------ #
# triangle particles

__custom_shape = [
    pgmath.Vector2(0, -1),
    pgmath.Vector2(1, 0),
    pgmath.Vector2(0.9, 0.15),
    pgmath.Vector2(0.8, 0.4),
    pgmath.Vector2(0.6, 0.7),
    pgmath.Vector2(0.5, 0.65),
    pgmath.Vector2(0.4, 0.5),
    pgmath.Vector2(0.2, 0.4),
    pgmath.Vector2(0, 0),

    pgmath.Vector2(-0.2, 0.4),
    pgmath.Vector2(-0.4, 0.5),
    pgmath.Vector2(-0.5, 0.65),
    pgmath.Vector2(-0.6, 0.7),
    pgmath.Vector2(-0.8, 0.4),
    pgmath.Vector2(-0.9, 0.15),
    pgmath.Vector2(-1, 0)

]


def create_custom_particle(parent, **kwargs):
    """Create a square particle"""
    r = kwargs["radius"] if "radius" in kwargs else 10
    return [parent.position.xy, 
            kwargs["vel"] if "vel" in kwargs else pgmath.Vector2((random.random()-0.5)*100, (random.random()-0.5)*100),
            0, # angle,
            kwargs["angv"] if "angv" in kwargs else (random.random()-0.5) * 1000,
            list(kwargs["color"]) if "color" in kwargs else [255, 192, 203],
            kwargs["life"] if "life" in kwargs else 1.0,
            tuple([_ * r for _ in __custom_shape]), # points
            parent.get_new_particle_id()]


def update_custom_particle(parent, particle):
    """Update a square particle"""
    # check if the particle is dead
    particle[5] -= soragl.SoraContext.DELTA
    # print(particle)
    if particle[5] <= 0:
        parent.remove_particle(particle)
        return
    # set color value
    particle[4][0] = 255 - abs(int(math.sin(particle[0].y) * 100))
    particle[4][1] = abs(int(math.cos(soragl.SoraContext.ENGINE_UPTIME) * 129))
    particle[4][2] = 200 - abs(int(math.sin(particle[0].x) * 40))
    # just spin + move in random direction
    particle[0] += particle[1] * soragl.SoraContext.DELTA
    particle[2] += particle[3] * soragl.SoraContext.DELTA
    # render -- square (that rotates)
    points = [i.rotate(particle[2]) + particle[0] for i in particle[6]]
    pgdraw.polygon(soragl.SoraContext.FRAMEBUFFER, particle[4], points, 1)


# register
physics.ParticleHandler.register_create_function("custom", create_custom_particle)
physics.ParticleHandler.register_update_function("custom", update_custom_particle)









print("More objects to be added! base_objects.py")

