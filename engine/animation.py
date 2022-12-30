import engine
import pygame
import json
import os

from engine import misc

# ------------------------------ #
# frame data

class FrameData:
    def __init__(self, frame: int, duration: float, order: int):
        self.frame = frame
        self.duration = duration
        self.order = order

    def get_rotated_frame(self, angle: float):
        """Get a rotated version of the frame"""
        return pygame.transform.rotate(self.frame, angle)
    
    def get_scaled_frame(self, scale: float):
        """Get a scaled version of the frame"""
        return pygame.transform.scale(self.frame, scale)
    
    def get_rotated_scaled_frame(self, angle: float, scale: float):
        """Get a rotated and scaled version of the frame"""
        return pygame.transform.rotozoom(self.frame, angle, scale)


# ------------------------------ #
# frame registry

class SequenceRegistry:
    def __init__(self, parent):
        """Allows access to animation sequence"""
        self.parent = parent
        self.findex = 0
        self.f = 0
        self.fdata = parent.get_frame(self.f)
        self.timer = engine.SoraContext.get_timer(limit=self.fdata.duration, loop=True)

    def update(self):
        self.timer.update()
        if self.timer.loopcount:
            self.f += 1
            self.f %= len(self.parent)
            self.fdata = self.parent.get_frame(self.f)
            self.timer.reset_timer(self.fdata.duration)
    
    def get_frame(self):
        """Get the current animation frame"""
        return self.fdata.frame


# ------------------------------ #
# sequence

class Sequence:
    # ------------------------------ #
    # animation sequence
    def __init__(self, frames: list, metadata: dict):
        # cannot manipulate this
        self._frames = frames
        self.duration = sum([f.duration for f in frames])
        self._metadata = metadata

    def get_frame(self, index: int):
        """Get a frame at a specified index"""
        return self._frames[index]
    
    def get_duration(self):
        """Get the total duration of the animation sequence"""
        return self.duration

    def __len__(self):
        """Get the number of frames in the sequence"""
        return len(self._frames)

    def __iter__(self):
        """Iterate over the frames in the sequence"""
        return iter(self._frames)
    
    def get_registry(self):
        """Get a sequence registry"""
        return SequenceRegistry(self)


# ------------------------------ #
# animation categories

class Category:
    SEQUENCES = {}

    @classmethod
    def load_category(cls, filename: str):
        """Load animation category"""
        meta, pframe = cls.load_from_dict(json.loads(misc.fread(filename)), os.path.dirname(filename))
        sequences = {}
        for each in pframe:
            sequences[each] = Sequence(pframe[each], meta)
        cls.SEQUENCES[filename] = {"meta": meta, "framedata": sequences}
    
    @classmethod
    def get_category_framedata(cls, filename: str):
        """Return the animation parsed framedata"""
        return cls.SEQUENCES[filename]["framedata"]
    
    @classmethod
    def get_category_metadata(cls, filename: str):
        """Return the animation metadata"""
        return cls.SEQUENCES[filename]["meta"]

    @classmethod
    def load_from_dict(cls, data: dict, parent_folder: str):
        """
        Load a sequence given data
        Format (aseprite):
        - frames
        - meta
        """
        meta = data["meta"]
        frames = data["frames"]
        # parse frames
        pframes = {}
        spritesheet = engine.SoraContext.load_image(os.path.join(parent_folder, meta["image"]))
        for f in frames:
            name = f["filename"]
            frame = f["frame"]
            sprite_source_size = f["spriteSourceSize"]
            source_size = f["sourceSize"]
            duration = f["duration"] / 1000
            # parse name string
            cat, ani, fnum = ".".join(name.split('.')[:-1]).split('-')
            fnum = int(fnum)
            if ani == '':
                ani = 'default'

            # extract frame data --> yeet into pygame surfacea
            surf = spritesheet.subsurface((frame['x'], frame['y']), (frame['w'], frame['h']))
            # make framedata -- other data kept out because unnecassary
            fdata = FrameData(surf, duration, fnum)
            # input into pframes
            if not ani in pframes:
                pframes[ani] = []
            pframes[ani].append(fdata)
        # return pframe
        return (meta, pframes)
        # if cat not in cls.SEQUENCES:
        #     cls.SEQUENCES[cat] = pframes
        # for key in pframes:
        #     cls.SEQUENCES[key] = pframes[key]





