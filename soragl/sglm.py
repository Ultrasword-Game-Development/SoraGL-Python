# ------------------------------------------------------------ #
# glm but in python :D + linting 
# ------------------------------------------------------------ #

from typing import *
import numpy as np

# ------------------------------ #
# default matrices

def identity_matrix():
    """Return the identity matrix"""
    return np.identity(4, dtype=np.float32)

def zero_matrix():
    """Return the zero matrix"""
    return np.zeros((4, 4), dtype=np.float32)

def translation_matrix(x: float, y: float, z: float):
    """Return the translation matrix"""
    return np.array([
        [1.0, 0.0, 0.0, x],
        [0.0, 1.0, 0.0, y],
        [0.0, 0.0, 1.0, z],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)

def scale_matrix(x: float, y: float, z: float):
    """Return the scale matrix"""
    return np.array([
        [x, 0.0, 0.0, 0.0],
        [0.0, y, 0.0, 0.0],
        [0.0, 0.0, z, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)

def rotation_matrix(angle: float, x: float, y: float, z: float):
    """Return the rotation matrix"""
    c = np.cos(angle)
    s = np.sin(angle)
    t = 1 - c
    return np.array([
        [t*x*x + c, t*x*y - s*z, t*x*z + s*y, 0.0],
        [t*x*y + s*z, t*y*y + c, t*y*z - s*x, 0.0],
        [t*x*z - s*y, t*y*z + s*x, t*z*z + c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)

def perspective_matrix(fov: float, aspect: float, near: float, far: float):
    """Return the perspective matrix"""
    f = 1.0 / np.tan(fov / 2.0)
    return np.array([
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0.0, 0.0, -1.0, 0.0],
    ], dtype=np.float32)

def orthographic_matrix(left: float, right: float, bottom: float, top: float, near: float, far: float):
    """Return the orthographic matrix"""
    return np.array([
        [2 / (right - left), 0.0, 0.0, -(right + left) / (right - left)],
        [0.0, 2 / (top - bottom), 0.0, -(top + bottom) / (top - bottom)],
        [0.0, 0.0, -2 / (far - near), -(far + near) / (far - near)],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)

def look_at(eye: np.ndarray, center: np.ndarray, up: np.ndarray):
    """Return the look at matrix"""
    f = (center - eye) / np.linalg.norm(center - eye)
    s = np.cross(f, up) / np.linalg.norm(np.cross(f, up))
    u = np.cross(s, f)
    return np.array([
        [s[0], u[0], -f[0], 0.0],
        [s[1], u[1], -f[1], 0.0],
        [s[2], u[2], -f[2], 0.0],
        [-np.dot(s, eye), -np.dot(u, eye), np.dot(f, eye), 1.0],
    ], dtype=np.float32)

# ------------------------------ #
# matrix to opengl

def matrix_to_opengl(matrix: np.ndarray):
    """Convert a matrix to opengl format"""
    return matrix.tobytes()

# ------------------------------ #





