import engine
import pygame

# ------------------------------ #
# frame data

class FrameData:
    # ------------------------------ #
    # frame data
    def __init__(self, frame: int, duration: float):
        self.frame = frame
        self.duration = duration

    def get_rotated_frame(self, angle: double):
        """Get a rotated version of the frame"""
        return pygame.transform.rotate(self.frame, angle)
    
    def get_scaled_frame(self, scale: double):
        """Get a scaled version of the frame"""
        return pygame.transform.scale(self.frame, scale)
    
    def get_rotated_scale(self, angle: double, scale: double):
        """Get a rotated and scaled version of the frame"""
        return pygame.transform.rotozoom(self.frame, angle, scale)


# ------------------------------ #
# animation dataset

class Sequence:
    # ------------------------------ #
    # animation sequence
    def __init__(self, frames: list, loop: bool):
        self.frames = frames
        self.loop = loop

    def get_frame(self, index: int):
        """Get a frame from the sequence"""
        return self.frames[index]

    def get_length(self):
        """Get the length of the sequence"""
        return len(self.frames)

    def get_duration(self):
        """Get the duration of the sequence"""
        duration = 0
        for frame in self.frames:
            duration += frame.duration
        return duration

    def get_frame_at_time(self, time: float):
        """Get a frame at a specific time"""
        duration = 0
        for frame in self.frames:
            duration += frame.duration
            if duration >= time:
                return frame
        return self.frames[-1]

    def get_frame_at_time_loop(self, time: float):
        """Get a frame at a specific time with looping"""
        duration = 0
        for frame in self.frames:
            duration += frame.duration
            if duration >= time:
                return frame
        return self.frames[0]

    def get_frame_at_time_clamp(self, time: float):
        """Get a frame at a specific time with clamping"""
        duration = 0
        for frame in self.frames:
            duration += frame.duration
            if duration >= time:
                return frame
        return self.frames[-1]

    def get_frame_at_time_loop_clamp(self, time: float):
        """Get a frame at a specific time with looping and clamping"""
        duration = 0
        for frame in self.frames:
            duration += frame.duration
            if duration >= time:
                return frame
        return self.frames[0]




# ------------------------------ #

class Animation:
    # ------------------------------ #
    # 
    pass

