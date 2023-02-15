import os

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
    @classmethod
    def find_file_ext(cls, path: str, ext: str):
        """Find file with given ext"""
        for f in os.listdir(path):
            if f.endswith(ext):
                return os.path.join(path, f)

    @classmethod
    def find_files_with_ext(cls, path: str, ext: list):
        """Find all files with ext - in dir"""
        for f in os.listdir(path):
            for j in ext:
                if f.endswith(j):
                    yield os.path.join(path, f)
                    break

    # ------------------------------ #

    def __init__(self, path: str):
        self._path = path

        # load data into buffers
        self._textures = mgl.TextureHandler()
        self._vao = mgl.VAO()
        self._vbo = mgl.Buffer("1f", [1.0])

    def load(self):
        """Load the model from the file path."""
        pass


# ------------------------------ #
# .obj


class MTLObjLoader(Loader):
    # ------------------------------ #

    MTL_EXT: str = ".mtl"
    OBJ_EXT: str = ".obj"
    IMG_EXT: list = [".jpg", ".png"]

    def __init__(self, path: str):
        """
        MTL object loader
        - all files should be found in a folder
        - textues + .mtl + .obj all found in root folder
        """
        super().__init__(path)
        # load the path -- find source folder or textures folder
        _dir = os.listdir(path)
        # find certain files
        self._obj = Loader.find_file_ext(path, self.OBJ_EXT)
        # load all textures
        for f in Loader.find_files_with_ext(path, self.IMG_EXT):
            self._textures.create_and_add_texture(f)
        # config for mtl file
        self._config = {}

    def load(self):
        """Load the mtl + obj file data"""
        # load obj file
        with open(self._obj, "r") as file:
            data = file.read()
        for line in data.split("\n"):
            if not line or line[0] == "#":
                continue
            if line.startswith("mtllib"):
                # load mtl file
                self.load_mtl(os.path.join(self.path, line.split()[1]))
            # parsing
            if line[0] == "o":
                pass
            elif line[0] == "v":
                pass
            elif line.startswith("vt"):
                pass
            elif line.startswith("vn"):
                pass
            print(line)

    def load_mtl(self, path: str):
        """Load an mtl file"""
        # load mtl file
        with open(self._mtl, "r") as file:
            # load data
            pass
