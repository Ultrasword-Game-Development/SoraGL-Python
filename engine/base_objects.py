import engine
from engine import scene, physics, mgl, animation

# ------------------------------ #
# base aspect objects

class MovementAspect:
    def __init__(self):
        self.priority = 0
        self.world = None
    
    def handle(self):
        """Handle movement for entities"""
        pass


