import os

import soragl
from soragl import mgl

import glm


# ------------------------------ #
# model class


class Face:
    def __init__(self, v1: list, v2: list, v3: list):
        """Face object for .obj files"""
        self._v1 = v1
        self._v2 = v2
        self._v3 = v3

    def __iter__(self):
        """Iterate over vertices"""
        yield self._v1
        yield self._v2
        yield self._v3

    def __getitem__(self, index: int):
        """Get vertex at index"""
        if index == 0:
            return self._v1
        elif index == 1:
            return self._v2
        elif index == 2:
            return self._v3
        else:
            raise IndexError("Index out of range")


class Model:
    def __init__(self, vbuffer, texture):
        """Model object"""
        self._vbuffer = vbuffer
        self._texture = texture


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
            elif line[0] == "o":
                # if has old
                if current_object:
                    objects[current_object] = reference
                # make new
                current_object = line.split()[1]
                # new obj -- 0 = vertices, 1 = uv, 2 = normal, 3 = faces
                reference = ([], [], [], [])
                objects[current_object] = reference
            elif line.startswith("vt"):
                vt = tuple(map(float, line.split()[1:]))
                reference[1].append(vt)
            elif line.startswith("vn"):
                vn = tuple(map(float, line.split()[1:]))
                reference[2].append(vn)
            elif line[0] == "v":
                v = tuple(map(float, line.split()[1:]))
                reference[0].append(v)
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
                # 0, 1, 2 || 2, 3, 0
                # add 2 Face objects to reference in above order
                reference[3].append(Face(face[0], face[1], face[2]))
                reference[3].append(Face(face[2], face[3], face[0]))
        objects[current_object] = reference

        # iterate thorugh each of the remaeining objects and construct the vertex buffer using the data found in the faces
        for name, data in objects.items():
            # get data
            vertices, uvs, normals, faces = data
            print("Finish texture laoding + mtl")
            textures = []
            # create buffer
            buffer = []
            for face in faces:
                for vertex in face:
                    # get vertex data
                    v = vertices[vertex[0] - 1]
                    vt = uvs[vertex[1] - 1]
                    vn = normals[vertex[2] - 1]
                    # add to buffer
                    buffer.extend(v)
                    buffer.extend(vt)
                    buffer.extend(vn)
            # add to results
            vertex_buffer = mgl.Buffer(f"{len(buffer)}f", buffer)
            self._results[name] = Model(vertex_buffer, textures)
        return self._results

    def load_mtl(self, path: str):
        """Load an mtl file"""
        # load mtl file
        with open(path, "r") as file:
            # load data
            pass

    def get_object(self, name: str):
        """Get an object by name"""
        return self._results[name]
