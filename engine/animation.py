import engine
import pygame

# ------------------------------ #
# frame data

class FrameData:
    def __init__(self, frame: int, duration: float):
        self.frame = frame
        self.duration = duration

    def get_rotated_frame(self, angle: float):
        """Get a rotated version of the frame"""
        return pygame.transform.rotate(self.frame, angle)
    
    def get_scaled_frame(self, scale: float):
        """Get a scaled version of the frame"""
        return pygame.transform.scale(self.frame, scale)
    
    def get_rotated_scale(self, angle: float, scale: float):
        """Get a rotated and scaled version of the frame"""
        return pygame.transform.rotozoom(self.frame, angle, scale)


# ------------------------------ #
# frame registry

class SequenceRegistry:
    def __init__(self, parent):
        """Allows access to animation sequence"""
        self.parent = parent
        self.findex = 0
        self.timer = engine.SoraContext.Timer()


# ------------------------------ #
# sequence

class Sequence:
    # ------------------------------ #
    # animation sequence
    def __init__(self, frames: list):
        self.frames = frames

    def get_frame(self, index: int):
        """Get a frame at a specified index"""
        return self.frames[index]

    def __len__(self):
        """Get the number of frames in the sequence"""
        return len(self.frames)

    def __iter__(self):
        """Iterate over the frames in the sequence"""
        return iter(self.frames)



# ------------------------------ #

class Animation:
    # ------------------------------ #
    # 
    pass

