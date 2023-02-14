import soragl
from soragl import mgl


# ------------------------------ #
# model class


class Model:
    def __init__(self):
        pass


# ------------------------------------------------------------ #
# model loader --
"""
For loading models
- .obj
- to add more
"""
# ------------------------------------------------------------ #


# loading models
class Loader:
    def __init__(self, path: str):
        self._path = path
        with open(path, "r") as file:
            self._data = file.read()

        # load data into buffers
        self.textures = []
        self.vao = mgl.VAO()
        self.vbo = mgl.VBO()

    def load(self):
        """Load the model from the file path."""
        pass


# ------------------------------ #
# .obj


class ObjLoader(Loader):
    def __init__(self, path: str):
        super().__init__(path)

    def load(self):
        pass
