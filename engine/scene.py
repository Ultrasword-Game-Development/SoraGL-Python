print("Activating scene.py!")

from queue import deque

# ------------------------------ #
# scenehandler

class SceneHandler:
    def __init__(self):
        self._stack = deque()
    
    def push_scene(self, scene):
        """Add a scene to the stack"""
        self._stack.append(scene)
    
    def pop_scene(self, scene):
        """Pop a scene from the stack"""
        self._stack.pop()
    
    def clear_stack(self):
        """Clear the scene stack"""
        self._stack.clear()


# ------------------------------ #
# scene -- handlers

class EntityHandler:
    ENTITY_TYPES = {}

    @classmethod
    def register_type(cls, ename, etype):
        """Register the entity type"""
        cls.ENTITY_TYPES[ename] = etype

    # ------------------------------ #

    def __init__(self):
        self._entities = {}

# ------------------------------ #
# scene -- world!

class World:
    def __init__(self):
        self.chunks = {}


class Chunk:
    def __init__(self, x: int, y: int):
        self._hash = f"{x}-{y}"
        self._intrinstic_entities = set()
        self.area = pygame.Rect()

    def __hash__(self):
        """Hash the chunk"""
        return hash(self._hash)
    
    





