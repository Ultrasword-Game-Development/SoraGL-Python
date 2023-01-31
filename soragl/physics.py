print("Activating physics.py")

import soragl
import random
import math

from soragl import scene
from pygame import Rect as pRect
from pygame import math as pgmath
from pygame import draw as pgdraw

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
    ENTITY_COUNT = 0

    def __init__(self):
        # defined after register
        self.world = None
        self.handler = None

        # private
        self._components = {}
        self._alive = True
        Entity.ENTITY_COUNT += 1
        self._entity_id = Entity.ENTITY_COUNT
        self._projected_position = pgmath.Vector2()

        # public
        self.c_chunk = [0, 0]
        self.position = pgmath.Vector2()
        self.velocity = pgmath.Vector2()
        self.rect = pRect(0, 0, 0, 0)

    # whenever components are added -- the world must be queried --> so that cache can be updated
    def on_ready(self):
        """When Entity is ready -- called at end of every update loop by world -- if new entity"""
        # print(self)
        pass

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
        pass
    
    def entity_has_component(self, comp_class):
        """Check if an entity has a component"""
        return hash(comp_class) in self._components

    def kill(self):
        """Kill the entity"""
        self._alive = False

    def __eq__(self, o):
        """Overload the == operator"""
        return id(self) == id(o)
    
    def __hash__(self):
        """Overload the hash operator"""
        return self._entity_id


# ------------------------------------------------------------ #
# collision data
# ------------------------------------------------------------ #

class Collision:
    def __init__(self, ec1, ec2):
        """Create a collision object"""
        entity1, entity2 = ec1._entity, ec2._entity
        # private
        h1, h2 = hash(entity1), hash(entity2)
        self._id_sum = (min(h1, h2) << 16) + max(h1, h2)

        # public
        self.entity1 = entity1
        self.entity2 = entity2
        self.shape1 = ec1
        self.shape2 = ec2
        self.dvec = self.entity1.position - self.entity2.position
        self.collisiontype = (hash(ec1.__class__), hash(ec2.__class__))
        self.intersect1 = (get_interval(self.shape1, RIGHT), get_interval(self.shape1, UP))
        self.intersect2 = (get_interval(self.shape2, RIGHT), get_interval(self.shape2, UP))
        # the rest of the data is to be calculated

    
    def get_intersects(self):
        """Get the intersects of the collision"""
        yield self.intersect1[0], self.intersect2[0]
        yield self.intersect1[1], self.intersect2[1]

    def __hash__(self):
        """Overload the 'id' operator"""
        return self._id_sum


# ------------------------------------------------------------ #
# collision objects
# ------------------------------------------------------------ #

class CollisionShape(scene.Component):
    COLLISIONSHAPE = True

    def __init__(self):
        super().__init__()
    
    def iterate_vertices(self):
        yield (0, 0)
    
    def iterate_vertices_relative(self):
        """Iteratore for relative vertices"""
        for v in self.iterate_vertices():
            yield self._entity.position + v
    
    def iterate_vertices_relative_projected(self):
        """Iterator for projected relative vertices"""
        for v in self.iterate_vertices_relative():
            yield self._entity._projected_position + v

    def get_vertices(self):
        """Get the vertices of the box"""
        return list(self.iterate_vertices())
    
    def get_support(self, dvec: pgmath.Vector2):
        """Get the support vector - position - greatest dis point from an axis"""
        highest = -1e9
        support = pgmath.Vector2()
        for v in self.get_vertices():
            dot = dvec.dot(v)
            if dot > highest:
                highest = dot
                support = v
        return support
    
    def get_isupport(self, dvec: pgmath.Vector2):
        """Get the reverse support vector - position - lowest dis from an axis"""
        lowest = 1e9
        support = pgmath.Vector2()
        for v in self.get_vertices():
            dot = dvec.dot(v+self._entity.position)
            if dot < lowest:
                lowest = dot
                support = v
        return support

    def get_projected_vertices(self):
        """Get the projected vertices of the box"""
        return [self._entity._projected_position + v for v in self.iterate_vertices()]
    
    def get_projected_support(self, dvec: pgmath.Vector2):
        """Get the projected support vector - position - greatest dis point from an axis"""
        highest = -1e9
        support = pgmath.Vector2()
        for v in self.get_projected_vertices():
            dot = dvec.dot(v)
            if dot > highest:
                highest = dot
                support = v
        return support
    
    def get_projected_isupport(self, dvec: pgmath.Vector2):
        """Get the projected reverse support vector - position - lowest dis from an axis"""
        lowest = 1e9
        support = pgmath.Vector2()
        for v in self.get_projected_vertices():
            dot = dvec.dot(v)
            if dot < lowest:
                lowest = dot
                support = v
        return support


class ConvexShape(CollisionShape):
    @classmethod
    def quickhull(cls, points):
        """Generate a convex hull from a list of points"""
        # worse case O(nlog(r)) time
        # n = number of input
        # r = num of processed
        hull = []
        # step 1: find points with min and max x coordinates
        points.sort(key=lambda p: (p.x, p.y))
        pmin, pmax = points[0], points[-1]
        result += [pmin, pmax]
        # step 2: split into 2 sections
        line = pmax - pmin
        s1, s2 = [], []
        for p in points:
            # determine if left or right of line
            c = line.cross(p)
            s1.append(p) if c > 0 else s2.append(p)
        # find hull
        cls.findhull(s1, pmin, pmax)
        cls.findhull(s2, pmax, pmin)
        return hull

    @classmethod
    def findhull(cls, points, p1, p2):
        """Find the convex hull of a set of points"""
        # base case
        if not points:
            return
        # find furthest point from: sample point
        line = p2 - p1
        p3 = max(points, key=lambda p: line.cross(p))
        # split into 3 subsets
        l1 = p3 - p1
        l2 = p2 - p3
        # find points inside
        i = 0
        s0, s1, s2 = [], [], []
        for p in points:
            # if inside
            if p.x < p3.x and l1.cross(p) > 0:
                s1.append(p)
            elif p.x > p3.x and l2.cross(p) > 0:
                s2.append(p)
            else:
                s0.append(p)
        print(s0, s1, s2)

    # https://en.wikipedia.org/wiki/Convex_hull
    # https://en.wikipedia.org/wiki/Quickhull#Pseudocode_for_2D_set_of_points
    # ------------------------------ #

    def __init__(self):
        super().__init__()



"""
https://www.toptal.com/game/video-game-physics-part-ii-collision-detection-for-solid-objects
TODO:
1. suports
2. aabb vs aabb / aabb vs box2d
3. circles + aabb / circles + box2d
4. box2d + box2d
5. minkowski sums! + differences
6. simplexes!
7. gjk algorithm!
8. penetration stuff
9. collision handling / resolving
10. ez
"""


class AABB(CollisionShape):
    """
    AABB = square that moves --> no rotation
    """
    def __init__(self, width: int, height: int, offx: int = 0, offy: int = 0):
        super().__init__()
        self._rect = pRect(offx, offy, width, height)
    
    def iterate_vertices(self):
        """Iterator for vertices"""
        yield self._entity.position + self._rect.topleft
        yield self._entity.position + self._rect.topright
        yield self._entity.position + self._rect.bottomleft
        yield self._entity.position + self._rect.bottomright


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
        center = pgmath.Vector2(self._rect.centerx, self._rect.centery)

        # get the vertices
        vertices = [
            pgmath.Vector2(self._rect.topleft) - center,
            pgmath.Vector2(self._rect.topright) - center,
            pgmath.Vector2(self._rect.bottomleft) - center,
            pgmath.Vector2(self._rect.bottomright) - center
        ]

        # rotate each vertex around the center
        for vertex in vertices:
            yield vertex.rotate(self._angle) + self._entity.position


# ------------------------------------------------------------ #
# SAT helper functions
# ------------------------------------------------------------ #

# interval functions
# https://github.com/codingminecraft/MarioYoutube/blob/265780291acc7693816ff2723c227ae89a171466/src/main/java/physics2d/rigidbody/IntersectionDetector2D.java
# sat calculations sorta

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

def project_point_to_axis(point, axis):
    """Project a point onto an axis"""
    return axis.rotate(90).dot(point)

def get_interval(comp, axis):
    """Get the interval of an AABB"""    
    result = pgmath.Vector2(0, 0)
    # axis.rotate_ip(90)
    points = comp.get_vertices()
    result.x = project_point_to_axis(points[0], axis)
    result.y = result.x
    for point in points[1:]:
        # ang = axis.angle_to(point)
        projection = project_point_to_axis(point, axis)
        if projection < result.x:
            result.x = projection
        if projection > result.y:
            result.y = projection
    return result


# ------------------------------------------------------------ #
# overlapping axis
# ------------------------------------------------------------ #

OVERLAP_FUNC = {}

def check_overlap(a, b, axis):
    """Check if two objects overlap on an axis"""
    # print(OVERLAP_FUNC)
    return OVERLAP_FUNC[(hash(a.__class__), hash(b.__class__))](a, b, axis)


def register_overlap_function(comp_class_a, comp_class_b, func):
    """Register an overlap function"""
    OVERLAP_FUNC[(hash(comp_class_a), hash(comp_class_b))] = func
    OVERLAP_FUNC[(hash(comp_class_b), hash(comp_class_a))] = func


# ------------------------------ #
# overlap functions

def overlap_AABBtoAABB(a, b, axis):
    """Check if two objects overlap on an axis"""
    # project points onto an axis then compare
    i1 = get_interval(a, axis)
    i2 = get_interval(b, axis)
    # print(id(a), id(b), i1, i2, end=" | ")
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
# handle collisions
# ------------------------------------------------------------ #

HANDLE_FUNC = {}

def register_handle_function(comp_class_a, comp_class_b, func):
    """Register a collision function"""
    HANDLE_FUNC[(hash(comp_class_a), hash(comp_class_b))] = func
    HANDLE_FUNC[(hash(comp_class_b), hash(comp_class_a))] = func


def resolve_collision(collision):
    """Resolve a collision between two objects"""
    return HANDLE_FUNC[collision.collisiontype](collision)

# ------------------------------ #
# resolving function

def handle_AABBtoAABB(collision):
    """Handle a collision between two AABBs"""
    penetration = float('inf')
    for i1, i2 in collision.get_intersects():
        # Calculate the normal of the collision
        normal = collision.entity2.position - collision.entity1.position
        if not normal: return 
        normal.normalize_ip()

        # Calculate the relative velocity of the objects
        rel_velocity = collision.entity2.velocity - collision.entity1.velocity

        # Calculate the impulse scalar
        impulse_scalar = rel_velocity.dot(normal) / normal.dot(normal)

        # Calculate the impulse vector
        impulse = normal * impulse_scalar

        # Apply the impulse to each object
        collision.entity1.velocity -= impulse
        collision.entity2.velocity += impulse

        # Move each object away from the other along the normal by the penetration depth
        correction = normal * (penetration / 2.0)
        collision.entity1.position -= correction
        collision.entity2.position += correction

def handle_AABBtoBox2D(collision):
    pass

# register the functions

register_handle_function(AABB, AABB, handle_AABBtoAABB)
register_handle_function(AABB, Box2D, handle_AABBtoBox2D)

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
        return cls.UPDATE[name] if name in cls.UPDATE else cls.UPDATE[cls.DEFAULT_UPDATE]
    
    @classmethod
    def get_create_timer_funcion(cls, name):
        """Get a timer function"""
        return cls.TIMER_FUNC[name] if name in cls.TIMER_FUNC else cls.TIMER_FUNC[cls.DEFAULT_TIMER]
    
    # ------------------------------ #

    def __init__(self, args: dict = {}, max_particles: int = 100, create_func: str = None, update_func: str = None, create_timer_func: str = None):
        super().__init__()
        # private
        self._particles = {}
        self._particle_count = 0
        self._max_particles = max_particles
        self._data = {
            "interval": 0.1
        }
        self._timer = 0
        self._remove = []
        self.args = args

        # public
        self._function_data = [create_func, update_func, create_timer_func]
        self.create_timer_func = ParticleHandler.get_create_timer_funcion(name=create_timer_func)
        self.create_func = ParticleHandler.get_create_function(name=create_func)
        self.update_func = ParticleHandler.get_update_function(name=update_func)
    
    def get_new_particle_id(self):
        """Get a new particle id"""
        self._particle_count += 1
        return self._particle_count

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
    
    def remove_particle(self, particle):
        """Remove a particle"""
        self._remove.append(particle[-1])

    def update(self):
        """Update the Particle Handler"""
        # print(self._function_data)
        self.create_timer_func(self)
        for particle in self._particles.values():
            self.update_func(self, particle)
        # remove timer
        for i in self._remove:
            del self._particles[i]
        # self._particle_count -= len(self._remove) # when removing particles bad things happen
        self._remove.clear()


# ------------------------------ #
# default for circle particles
# attribs = [pos, vel, radius, color, life]
# create function
def _default_create(parent, **kwargs):
    """Default create function for particles"""
    return [parent.position.xy, 
            kwargs["vel"] if "vel" in kwargs else pgmath.Vector2(random.random()-0.5, -5),
            kwargs["radius"] if "radius" in kwargs else 2, 
            kwargs["color"] if "color" in kwargs else (0, 0, 255),
            kwargs["life"] if "life" in kwargs else 1.0,
            parent.get_new_particle_id()]

# update function
def _default_update(parent, particle):
    """Default update function for particles"""
    # gravity
    particle[1] += GRAVITY * soragl.SoraContext.DELTA
    particle[4] -= soragl.SoraContext.DELTA
    if particle[4] <= 0:
        parent.remove_particle(particle)
        return
    # move
    particle[0] += particle[1]
    # render
    pgdraw.circle(soragl.SoraContext.FRAMEBUFFER, particle[3], particle[0], particle[2]) #, 1)

# timer function
def _default_timer(parent):
    """Default timer function for particles"""
    parent._timer += soragl.SoraContext.DELTA
    if parent._timer >= parent._data["interval"]:
        # print(parent._function_data)
        parent._timer = 0
        particle = parent.create_func(parent, **parent.args)
        # print("created particle")
        parent._particles[particle[-1]] = particle
        # print(parent._particle_count)

# update function
ParticleHandler.register_create_function(ParticleHandler.DEFAULT_CREATE, _default_create)
ParticleHandler.register_update_function(ParticleHandler.DEFAULT_UPDATE, _default_update)
ParticleHandler.register_timer_function(ParticleHandler.DEFAULT_TIMER, _default_timer)

