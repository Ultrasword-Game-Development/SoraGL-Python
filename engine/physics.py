print("Activating physics.py")

import engine

from engine import scene
from pygame import Rect as pRect
from pygame import math as pgmath

# ------------------------------------------------------------ #
# global constnats
# ------------------------------------------------------------ #

RIGHT = pgmath.Vector2(1, 0)
LEFT = pgmath.Vector2(-1, 0)
UP = pgmath.Vector2(0, -1)
DOWN = pgmath.Vector2(0, 1)

X_AXIS = RIGHT
Y_AXIS = UP

GRAVITY = DOWN * 9.8

# ------------------------------------------------------------ #
# create a base entity class using the entity system
# ------------------------------------------------------------ #

class Entity:
    def __init__(self):
        # defined after register
        self.world = None
        self.handler = None

        # private
        self._components = {}
        self._alive = True

        # public
        self.c_chunk = [0, 0]
        self.position = pgmath.Vector2()
        self.rect = pRect(0, 0, 0, 0)

    # whenever components are added -- the world must be queried --> so that cache can be updated

    @property
    def components(self) -> dict:
        """Components property"""
        return self._components
    
    def add_component(self, component):
        """Add a component to the entity"""
        self.world.add_component(self, component)
    
    def remove_component(self, component):
        """Remove a component from the entity"""
        if component in self._components:
            self.world.remove_component(self, component)
    
    def get_component_from_hash(self, comp_class_hash: int):
        """Get a component from the entity"""
        if comp_class_hash in self._components:
            return self._components[comp_class_hash]
        return None
    
    def get_component(self, comp_class):
        """Get a component from the entity"""
        return self.get_component_from_hash(hash(comp_class))

    def update(self):
        """Default update function"""
        # print(id(self))
        pass
    
    def entity_has_component(self, comp_class):
        """Check if an entity has a component"""
        return hash(comp_class) in self._components

    def kill(self):
        """Kill the entity"""
        self._alive = False

# ------------------------------------------------------------ #
# collision objects
# ------------------------------------------------------------ #

class CollisionShape(scene.Component):
    COLLISIONSHAPE = True
    def __init__(self):
        super().__init__()


class AABB(CollisionShape):
    """
    AABB = square that moves --> no rotation
    """
    def __init__(self, width: int, height: int, offx: int = 0, offy: int = 0):
        super().__init__()
        self._rect = pRect(offx, offy, width, height)
    
    def iterate_vertices(self):
        """Iterator for vertices"""
        yield self._entity.position + self.rect.topleft
        yield self._entity.position + self.rect.topright
        yield self._entity.position + self.rect.bottomleft
        yield self._entity.position + self.rect.bottomright

class Box2D(CollisionShape):
    """
    Box2D = square that moves + rotation
    """
    def __init__(self, width: int, height: int, offx: int = 0, offy: int = 0, degrees: float = 0):
        super().__init__()
        self._rect = pRect(offx, offy, width, height)
        self._angle = degrees
        self._center = self._rect.center
    
    @property
    def angle(self):
        """Angle property"""
        return self._angle
    
    @angle.setter
    def angle(self, value):
        """Angle setter"""
        self._angle = value

    @property
    def center(self):
        """Center property"""
        return self._center
    
    @center.setter
    def center(self, value):
        """Center setter"""
        self._center = value

    def iterate_vertices(self):
        """Iterator for rotated vertices"""
        # get the center of the rectangle
        center = pgmath.Vector2(self.rect.centerx, self.rect.centery)

        # get the vertices
        vertices = [
            pgmath.Vector2(self.rect.topleft) - center,
            pgmath.Vector2(self.rect.topright) - center,
            pgmath.Vector2(self.rect.bottomleft) - center,
            pgmath.Vector2(self.rect.bottomright) - center
        ]

        # rotate each vertex around the center
        for vertex in vertices:
            yield vertex.rotate(self._angle) + self._entity.position

# ------------------------------------------------------------ #
# SAT helper functions
# ------------------------------------------------------------ #

# interval functions

INTERVAL_FUNC = {}

def get_interval(comp, axis):
    """Get the interval of a component"""
    global INTERVAL_FUNC
    return INTERVAL_FUNC[hash(comp.__class__)](comp, axis)


def register_interval_function(comp_class, func):
    """Register an interval function"""
    global INTERVAL_FUNC
    INTERVAL_FUNC[hash(comp_class)] = func

# ------------------------------ #
# interval functions

def interval_aabb(comp, axis):
    """Get the interval of an AABB"""    
    result = pgmath.Vector2(0, 0)

    for point in comp.iterate_vertices():
        projection = axis.dot(point)
        if projection < result.x:
            result.x = projection
        if projection > result.y:
            result.y = projection
    return result


# dont know if necassary
# def interval_box2d(comp, axis):
#     """Get the interval of a Box2D"""
#     result = pgmath.Vector2(0, 0)

#     for point in comp.iterate_vertices():
#         projection = axis.dot(point)
#         if projection < result.x:
#             result.x = projection
#         if projection > result.y:
#             result.y = projection
#     return result

# ------------------------------ #
# register!

register_interval_function(AABB, interval_aabb)
register_interval_function(Box2D, interval_aabb) # inteval_box2d

# ------------------------------------------------------------ #
# overlapping axis
# ------------------------------------------------------------ #

OVERLAP_FUNC = {}

def register_overlap_function(comp_class_a, comp_class_b, func):
    """Register an overlap function"""
    OVERLAP_FUNC[(hash(comp_class_a.__class__), hash(comp_class_b.__class__))] = func
    OVERLAP_FUNC[(hash(comp_class_b.__class__), hash(comp_class_a.__class__))] = func


def overlap_AABBtoAABB(a, b, axis):
    """Check if two objects overlap on an axis"""
    # project points onto an axis then compare
    i1 = get_interval(a, axis)
    i2 = get_interval(b, axis)
    return i1.x <= i2.y and i2.x <= i1.y

# def overlap_AABBtoBox2D(a, b, axis):
#     """Check if two objects overlap on an axis"""
#     # project points onto an axis then compare
#     i1 = get_interval(a, axis)
#     i2 = get_interval(b, axis)
#     return i1.x <= i2.y and i2.x <= i1.y

# def overlap_Box2DtoBox2D(a, b, axis):
#     """Check if two objects overlap on an axis"""
#     # project points onto an axis then compare
#     i1 = get_interval(a, axis)
#     i2 = get_interval(b, axis)
#     return i1.x <= i2.y and i2.x <= i1.y


# ------------------------------ #
# register!

register_overlap_function(AABB, AABB, overlap_AABBtoAABB)
register_overlap_function(AABB, Box2D, overlap_AABBtoAABB)
register_overlap_function(Box2D, Box2D, overlap_AABBtoAABB)


# ------------------------------------------------------------ #
# particle handling + physics
# ------------------------------------------------------------ #

class ParticleHandler(Entity):
    # ------------------------------ #
    # functions for updating + creating particles

    CREATE = {}
    UPDATE = {}
    TIMER_FUNC = {}

    DEFAULT_CREATE = "default_create"
    DEFAULT_UPDATE = "default_update"
    DEFAULT_TIMER = "default_timer"

    @classmethod
    def register_create_function(cls, name, func):
        """Register a create function"""
        cls.CREATE[name] = func

    @classmethod    
    def register_update_function(cls, name, func):
        """Register an update function"""
        cls.UPDATE[name] = func

    @classmethod
    def register_timer_function(cls, name, func):
        """Register a timer function"""
        cls.TIMER_FUNC[name] = func
    
    @classmethod
    def get_create_function(cls, name):
        """Get a create function"""
        return cls.CREATE[name] if name in cls.CREATE else cls.CREATE[cls.DEFAULT_CREATE]
    
    @classmethod
    def get_update_function(cls, name):
        """Get an update fucntion"""
        return cls.UPDATE[name] if name in cls.UPDATE else cls.UDPATE[cls.DEFAULT_UPDATE]
    
    @classmethod
    def get_create_timer_funcion(cls, name):
        """Get a timer function"""
        return cls.TIMER_FUNC[name] if name in cls.TIMER_FUNC else cls.TIMER_FUNC[cls.DEFAULT_TIMER]
    
    # ------------------------------ #

    def __init__(self, max_particles: int = 100, create_func: str = None, update_func: str = None, create_timer_func: str = None):
        super().__init__()
        # private
        self._particles = {}
        self._particle_count = 0
        self._max_particles = max_particles
        self._data = {
            "interval": 0.1
        }
        self._timer = 0

        # public
        self.create_timer_func = ParticleHandler.get_create_timer_funcion(name=create_timer_func)
        self.create_func = ParticleHandler.get_create_function(name=create_func)
        self.update_func = ParticleHandler.get_update_function(name=update_func)

    @property
    def data(self):
        """Get the data for the particle handler"""
        return self._data

    def __getitem__(self, name):
        """Get a piece of data"""
        return self._data[name]
    
    def __setitem__(self, name, value):
        """Set a piece of data"""
        self._data[name] = value
    
    def update(self):
        """Update the Particle Handler"""
        self.create_timer_func(self)
        for particle in self._particles.values():
            self.update_func(self, particle)


# ------------------------------ #
# default for circle particles
# attribs = [pos, vel, radius, color, life]
# create function
ParticleHandler.register_create_function(ParticleHandler.DEFAULT_CREATE, 
            lambda parent, **kwargs: [parent.position.xy, 
                        kwargs["vel"] if "vel" in kwargs else pgmath.Vector2(), 
                        kwargs["radius"] if "radius" in kwargs else 5, 
                        kwargs["color"] if "color" in kwargs else (0, 0, 255), 
                        kwargs["life"] if "life" in kwargs else 1.0])

# update function
def _default_update(parent, particle):
    """Default update function for particles"""
    # gravity
    particle[1] += GRAVITY
    # move
    particle[0] += particle[1] * engine.SoraContext.DELTA
    particle[6] -= engine.SoraContext.DELTA
    if particle[6] <= 0:
        del parent._particles[particle]
        parent._particle_count -= 1
        return
    # render
    pgdraw.circle(engine.SoraContext.FRAMEBUFFER, particle[3], particle[0], particle[2]) #, 1)

# timer function
def _default_timer(parent):
    """Default timer function for particles"""
    parent._timer += engine.SoraContext.DELTA
    if parent._timer >= parent._data["interval"]:
        parent._timer = 0
        parent.create_func(parent)

# update function
ParticleHandler.register_update_function(ParticleHandler.DEFAULT_UPDATE, _default_update)
ParticleHandler.register_timer_function(ParticleHandler.DEFAULT_TIMER, _default_timer)

