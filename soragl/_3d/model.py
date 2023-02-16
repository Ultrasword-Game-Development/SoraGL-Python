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
        # results
        self._results = {}

    @property
    def results(self):
        """Get results"""
        return self._results

    @property
    def objects(self):
        """Get all object names"""
        return list(self._results.keys())

    def load(self):
        """Load the mtl + obj file data"""
        # load obj file -- http://web.cse.ohio-state.edu/~shen.94/581/Site/Lab3_files/Labhelp_Obj_parser.htm
        with open(self._obj, "r") as file:
            data = file.read()

        # data
        objects = {}
        current_object = None
        reference = None

        for line in data.split("\n"):
            if not line or line[0] == "#":
                continue
            if line.startswith("mtllib"):
                # load mtl file
                self.load_mtl(os.path.join(self._path, line.split()[1]))
            # parsing
            if line[0] == "o":
                # if has old
                if current_object:
                    objects[current_object] = reference
                # make new
                current_object = line.split()[1]
                # new obj -- 0 = vertices, 1 = uv, 2 = normal
                reference = ([], [], [], [])
                objects[current_object] = reference
            elif line[0] == "v":
                reference[0].append(list(map(float, line.split()[1:])))
            elif line.startswith("vt"):
                reference[1].append(list(map(float, line.split()[1:])))
            elif line.startswith("vn"):
                reference[2].append(list(map(float, line.split()[1:])))
            elif line.startswith("f"):
                # vertex/texture/normal -- texture + normal are optional
                # -1 == does not exist
                face = []
                for x in line.split()[1:]:
                    r = []
                    for i in x.split("/") + [""] * (3 - len(x.split("/"))):
                        if i == "":
                            continue
                        r.append(int(i))
                    face.append(r)
                reference[3].append(face)
            # print(line)
        print(objects)
        # finalizing data
        # create vao + ibo
        for name, vals in objects.items():
            # generate final objects
            vbuf = []
            ibuf = []
            for f in vals[3]:
                buf += 

            parse = f"{len(buf)}f"
            _vertex_buf = mgl.Buffer(parse, vbuf)
            _index_buf = mgl.Buffer(parse, ibuf)

    def load_mtl(self, path: str):
        """Load an mtl file"""
        # load mtl file
        with open(path, "r") as file:
            # load data
            pass
