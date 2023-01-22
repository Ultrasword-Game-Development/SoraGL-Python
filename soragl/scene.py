# ------------------------------------------------------------ #
import json
import pygame
# ------------------------------------------------------------ #
import soragl
if soragl.SoraContext.DEBUG:
    print("Activating scene.py")
from queue import deque
# ------------------------------------------------------------ #

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
        self._new_entities = set()
    
    def initialize_entities_at_end_of_update(self):
        """Initialize the entities at the end of the update"""
        for e in self._new_entities:
            self._entities[e].on_ready()
        self._new_entities.clear()

    def register_entity(self, entity):
        """Register the entity"""
        entity.handler = self
        entity.world = self._world
        # store entity in ehandler
        self._entities[hash(entity)] = entity
        self._new_entities.add(hash(entity))
    
    def get_entity(self, entity):
        """Get the entity"""
        return self._entities[hash(entity)]
    
    def remove_entity(self, entity):
        """Remove the entity"""
        del self._entities[hash(entity)]

    def clear(self):
        """Clear the entity handler"""
        self._entities.clear()


# ------------------------------ #
# scene - chunks

class Chunk:

    def __init__(self, x: int, y: int, world, options: dict):
        # private
        self._intrinstic_entities = set()
        self._hash = f"{x}-{y}"
        self._world = world
        
        # public
        cpw, cph = options["chunkpixw"], options["chunkpixh"]
        self.area = pygame.Rect(x * cpw, y * cph, (x+1) * cpw, (y+1) * cph)
        # print(self.area)

    def __hash__(self):
        """Hash the chunk"""
        return hash(self._hash)
    
    def update(self):
        """Update the chunk"""
        # update all intrinstic entities
        for entity in self._intrinstic_entities:
            self._world._ehandler._entities[entity].update()
            # print(self._world._ehandler._entities[entity].c_chunk)
        # debug update
        if soragl.SoraContext.DEBUG:
            pygame.draw.rect(soragl.SoraContext.FRAMEBUFFER, (255, 0, 0), self.area, 1)


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
    
    def on_add(self):
        """When added to the world"""
        pass

    def handle(self, *args, **kwargs):
        """base process function"""
        raise NotImplementedError("Process function not implemented")

    def iterate_entities(self):
        """Iterate through the entities"""
        # print(self._world._components[self._target])
        for entity in self._world._components[self._target]:
            yield self._world._ehandler._entities[entity]

# ------------------------------ #
# components

class ComponentHandler:
    COMPONENTS = {} # comp_hash: comp class

    @classmethod
    def register_component(cls, comp):
        """Register the component"""
        if comp.__class__.__name__ not in cls.COMPONENTS:
            cls.COMPONENTS[comp.__class__.__name__] = comp.__class__


class Component:
    def __init__(self, loaded_hash: int = None):
        """Create a component"""
        # private
        self._entity = None
        
        # public
        ComponentHandler.register_component(self)
        self.HASH = loaded_hash if loaded_hash != None else hash(self.__class__)
    
    def on_add(self):
        """When an added to an Entity"""
        pass

    def __hash__(self):
        """Hash the component"""
        return hash(self.__class__)
    
    def get_hash(self):
        """Get the pre-loaded hash"""
        return self.HASH

# ------------------------------ #
# world class

class World:
    """
    Acts as layers within a scene
    """

    def __init__(self, options: dict, render_distance: int = 1, aspects: dict = {}, chunks: dict={}):
        self._chunks = {}
        self._active_chunks = set()
        self._ehandler = EntityHandler(self)
        self._aspects = []
        self._components = {} # comp_hash: {entities} (set)
        self._options = options
        # rendering
        self._center_chunk = [0, 0]
        self._developer_data = {}

        # variables
        self.render_distance = render_distance
        self.aspect_times = {}
        
        # add data to buffer
        for i, j in aspects.items():
            self.add_aspect(i, j)
        for i, j in chunks.items():
            self.add_chunk(i, j)
        
        # update active chunks
        self.set_center_chunk(0, 0)

    def set_center_chunk(self, x: int, y: int):
        """Set the center chunk for rendering"""
        self._center_chunk[0] = x
        self._center_chunk[1] = y
        # update active chunks
        self._active_chunks.clear()
        for i in range(self._center_chunk[0] - self.render_distance, self._center_chunk[0] + self.render_distance + 1):
            for j in range(self._center_chunk[1] - self.render_distance, self._center_chunk[1] + self.render_distance + 1):
                self._active_chunks.add(hash(self.get_chunk(i, j)))

    def get_chunk(self, x: int, y: int):
        """Get the chunk"""
        f = hash(f"{x}-{y}")
        if f in self._chunks:
            return self._chunks[f]
        c = Chunk(x, y, self, self._options)
        self._chunks[hash(c)] = c
        return c

    def iter_active_entities(self):
        """Iterate through the active entities"""
        for chunk in self._active_chunks:
            for entity in self._chunks[chunk]._intrinstic_entities:
                yield self._ehandler._entities[entity]

    def get_entity(self, entity):
        """Get the entity"""
        return self._ehandler.get_entity(entity)

    def add_entity(self, entity):
        """Add an entity to the world"""
        self._ehandler.register_entity(entity)
        for comp in entity.components:
            self.add_component(entity, comp)
        # add to chunk
        self.get_chunk(0, 0)._intrinstic_entities.add(hash(entity))

    def update_entity_chunk(self, entity, old, new):
        """Update the chunk intrinsic properties for entities"""
        ochunk = self.get_chunk(old[0], old[1])
        nchunk = self.get_chunk(new[0], new[1])
        ochunk._intrinstic_entities.remove(hash(entity))
        nchunk._intrinstic_entities.add(hash(entity))
        entity.c_chunk[0], entity.c_chunk[1] = new

    def add_component(self, entity, component):
        """Add a component to an entity in the world"""
        comp_hash = hash(component)
        # print(component.__class__.__name__, comp_hash)
        if comp_hash not in self._components:
            self._components[comp_hash] = set()
        self._components[comp_hash].add(hash(entity))
        # add to entity
        entity._components[comp_hash] = component
        # component parent = entity
        component._entity = entity
        component.on_add()
        # print(self._components)
        
    def remove_component(self, entity, comp_class):
        """Remove a component from an entity"""
        if comp_class.get_hash() in self._components:
            self._components[comp_class.get_hash()].remove(hash(entity))
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
        aspect.on_add()
        self._aspects.sort(key=lambda x: x.priority, reverse=True)
        if aspect._target not in self._components:
            self._components[aspect._target] = set()
        # print("DEBUG: Aspect sorting", [x.priority for x in self._aspects])
        # print(self._aspects)
        # cache the components
        # self._components[aspect._target] = set()

    def get_aspect(self, aspect_class):
        """Get an aspect"""
        for i in self._aspects:
            if isinstance(i, aspect_class):
                return i
        return None

    def remove_aspect(self, aspect_type):
        """Remove a processor -- all instnaces of the same type"""
        for i in self._aspects:
            if isinstance(i, aspect_type):
                del i._world
                self._aspects.remove(i)

    def update(self):
        """Update the world"""
        # == update chunks
        for i in self._active_chunks:
            self._chunks[i].update()
        # for i in self._chunks.values():
        #     i.update()
        # == update aspects
        for aspect in self._aspects:
            aspect.handle()
        # TODO - do I want to stick with this??? 
        # keep chunks --> they update entities!
        
        # == initialize new entities
        self._ehandler.initialize_entities_at_end_of_update()

    def handle_aspects(self):
        """Handle the aspects"""
        for i in self._aspects:
            i.handle()

    def handle_aspect_timed(self) -> list:
        """Handle the aspects"""
        for i in self._aspects:
            st = soragl.SoraContext.get_time()
            i.handle()
            aspect_time = int(round((soragl.SoraContext.get_time() - st) * 1000, 3))
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
    DEFAULT_CONFIG = "assets/config.json"

    def __init__(self, config: dict = None):
        """Create a scene object"""
        # private
        self._layers = []
        self._config = config if config else load_config(Scene.DEFAULT_CONFIG)

        # public
        self.priority = 0
    
    def add_layer(self, layer: World, priority: int = 0):
        """Add a layer to the scene"""
        layer.priority = priority
        self._layers.append(layer)
        self._layers.sort(key=lambda x: x.priority, reverse=True)
    
    def remove_layer(self, layer: World):
        """Remove a layer from the scene"""
        self._layers.remove(layer)
    
    def get_config(self):
        """Get the scene configuration"""
        return self._config

    def update(self):
        """Update a scene"""
        # update layers
        for layer in self._layers:
            layer.update()

# ------------------------------ #

# configuration for ECS
DEFAULT_CONFIG = {"chunkpixw": 256, "chunkpixh": 256, "chunktilew": 16, "chunktileh": 16, "tilepixw": 16, "tilepixh": 16}

def configure_ecs(**kwargs):
    """Filter out invalid configurations"""
    # global DEFAULT_CONFIG
    config = {}
    for k, v in kwargs.items():
        if k in DEFAULT_CONFIG:
            config[k] = v
    # default values
    for each, val in DEFAULT_CONFIG.items():
        if each not in config:
            config[each] = val
    # calculate chunk pixel values
    config["chunkpixw"] = config["chunktilew"] * config["tilepixw"]
    config["chunkpixh"] = config["chunktileh"] * config["tilepixh"]

    return config

def save_config(config, fname):
    """Save a configuration for ECS"""
    with open(fname, 'w') as file:
        json.dump(file, config)

def load_config(fname):
    """Load a configuration for ECS"""
    with open(fname, 'r') as file:
        return configure_ecs(**json.load(file))
