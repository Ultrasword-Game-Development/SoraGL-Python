print("Activating physics.py")

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


