import engine
if engine.SoraContext.DEBUG:
    print("Activating scene.py")
from queue import deque


# ------------------------------ #
# scenehandler

class SceneHandler:
    _STACK = deque()
    CURRENT = None
    
    @classmethod
    def push_scene(cls, scene):
        """Add a scene to the stack"""
        CURRENT = scene
        cls._STACK.append(scene)
    
    @classmethod
    def pop_scene(cls, scene):
        """Pop a scene from the stack"""
        cls._STACK.pop()
    
    @classmethod
    def clear_stack(cls):
        """Clear the scene stack"""
        cls._STACK.clear()
        CURRENT = None
    
    @classmethod
    def update(cls):
        """Update the current scene"""
        cls._STACK[-1].update()


# ------------------------------ #
# scene -- handlers

class EntityHandler:
    """
    entity handlers:
    - only store entities + entity types
    - used to compare entity types + entities if required!
    """
    ENTITY_TYPES = {}

    @classmethod
    def register_type(cls, ename, etype):
        """Register the entity type"""
        cls.ENTITY_TYPES[ename] = etype

    # ------------------------------ #

    def __init__(self, world):
        self._entities = {}
        self._world = world
    
    def register_entity(self, entity):
        """Register the entity"""
        entity.handler = self
        entity.world = self._world
        self._entities[id(entity)] = entity
    
    def get_entity(self, eid):
        """Get the entity"""
        return self._entities[eid]
    
    def remove_entity(self, eid):
        """Remove the entity"""
        del self._entities[eid]

    def clear(self):
        """Clear the entity handler"""
        self._entities.clear()

# ------------------------------ #
# scene - chunks

class Chunk:
    def __init__(self, x: int, y: int):
        self._hash = f"{x}-{y}"
        self._intrinstic_entities = set()
        self.area = pygame.Rect()

    def __hash__(self):
        """Hash the chunk"""
        return hash(self._hash)
    
    def update(self):
        """Update the chunk"""
        pass


# ------------------------------ #
# scene - aspects

class Aspect:
    def __init__(self, target_component_class, priority:int=0):
        """Create a processor"""
        # defined after added to world
        self._world = None
        # variables
        self.priority = priority
        self._target = hash(target_component_class)
    
    def handle(self, *args, **kwargs):
        """base process function"""
        raise NotImplementedError("Process function not implemented")

    def iterate_entities(self):
        """Iterate through the entities"""
        for entity in self._world._components[self._target]:
            yield entity

# ------------------------------ #
# components

class ComponentHandler:
    COMPONENTS = {} # comp_hash: comp class

    @classmethod
    def register_component(cls, comp):
        """Register the component"""
        if hash(comp) not in cls.COMPONENTS:
            cls.COMPONENTS[hash(comp)] = comp.__class__


class Component:
    def __init__(self, loaded_hash: int = None):
        """Create a component"""
        # private
        self._entity = None
        
        # public
        ComponentHandler.register_component(self)
        self.HASH = loaded_hash if loaded_hash != None else hash(self)
        # print('component base class')
        # print(self.HASH)
        # print(hash(self))
    
    def on_add(self):
        """When an added to an Entity"""
        pass

    def __hash__(self):
        """Hash the component"""
        return hash(self.__class__.__name__)
    
    def get_hash(self):
        """Get the pre-loaded hash"""
        return self.HASH

# ------------------------------ #
# world class

class World:
    """
    Acts as layers within a scene
    """
    def __init__(self, render_distance: int = 1, aspects: dict = {}, chunks: dict={}):
        self._chunks = {}
        self._ehandler = EntityHandler(self)
        self._aspects = []
        self._components = {} # comp_hash: {entities} (set)

        # variables
        self.render_distance = render_distance
        self.aspect_times = {}
        
        # update data
        for i, j in aspects.items():
            self.add_aspect(i, j)
        for i, j in chunks.items():
            self.add_chunk(i, j)

    def add_entity(self, entity):
        """Add an entity to the world"""
        self._ehandler.register_entity(entity)
        for comp in entity.components:
            self.add_component(entity, comp)

    def add_component(self, entity, component):
        """Add a component to an entity in the world"""
        comp_hash = hash(component.__class__)
        if comp_hash not in self._components:
            self._components[comp_hash] = set()
        self._components[comp_hash].add(entity)
        # add to entity
        entity._components[comp_hash] = component
        component._entity = entity
        component.on_add()

    def remove_component(self, entity, comp_class):
        """Remove a component from an entity"""
        if comp_class.get_hash() in self._components:
            self._components[comp_class.get_hash()].remove(entity)
            entity.components.remove(comp_class.get_hash())

    def add_chunk(self, chunk_hash: int, chunk):
        """Add chunks to the world"""
        self._chunks[chunk_hash] = chunk

    def remove_chunk(self, chunk_hash: int):
        """Remove a chunk"""
        if chunk_hash in self._chunks:
            return self._chunks.pop(chunk_hash)
    
    def add_aspect(self, aspect):
        """Add an aspect to the world"""
        aspect._world = self
        self._aspects.append(aspect)
        self._aspects.sort(key=lambda x: x.priority, reverse=True)
        # print("DEBUG: Aspect sorting", [x.priority for x in self._aspects])
        # print(self._aspects)
    
    def remove_aspect(self, aspect_type):
        """Remove a processor -- all instnaces of the same type"""
        for i in self._aspects:
            if isinstance(i, aspect_type):
                del i._world
                self._aspects.remove(i)

    def update(self):
        """Update the world"""
        for i in self._chunks.values():
            i.update()
        # update aspects
        for aspect in self._aspects:
            aspect.handle()
        # TODO - do I want to stick with this??? 
        # keep chunks --> they update entities!

    def handle_aspects(self):
        """Handle the aspects"""
        for i in self._aspects:
            i.handle()
        
    def handle_aspect_timed(self) -> list:
        """Handle the aspects"""
        for i in self._aspects:
            st = engine.SoraContext.get_time()
            i.handle()
            aspect_time = int(round((engine.SoraContext.get_time() - st) * 1000, 3))
            self.aspect_times[i.__class__.__name__] = aspect_time

    def clear_world(self):
        """Clear all chunks + entities + aspects + processors"""
        self._chunks.clear()
        self._aspects.clear()
        self._ehandler.clear()

    def clear_cache(self):
        """Clear the cache"""
        self._components.clear()


# ------------------------------ #
# scene

class Scene:
    def __init__(self):
        """Create a scene object"""
        self._layers = []
        self.priority = 0
    
    def add_layer(self, layer: World, priority: int = 0):
        """Add a layer to the scene"""
        layer.priority = priority
        self._layers.append(layer)
        self._layers.sort(key=lambda x: x.priority, reverse=True)
    
    def remove_layer(self, layer: World):
        """Remove a layer from the scene"""
        self._layers.remove(layer)
    
    def update(self):
        """Update a scene"""
        for layer in self._layers:
            layer.update()

