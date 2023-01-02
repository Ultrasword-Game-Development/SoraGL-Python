print("Activating physics.py")

from pygame import math as pgmath

# create a base entity class using the entity system

class Entity:
    def __init__(self):
        # defined after register
        self.world = None
        self.handler = None

        # private
        self._components = {}

        # public
        self.position = pgmath.Vector2()
        self.velocity = pgmath.Vector2()

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
        pass
    





