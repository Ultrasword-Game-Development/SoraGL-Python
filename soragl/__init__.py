print("Thanks for using Sora Engine! v0.1")

import pygame
import time


class SoraContext:

    DEBUG = True

    # ------------------------------ #
    # time + time + time
    ENGINE_UPTIME = 0
    ENGINE_START_TIME = 0

    START_TIME = 0
    END_TIME = 0
    DELTA = 0

    @classmethod
    def start_engine_time(cls):
        """Starts engine time."""
        cls.ENGINE_START_TIME = time.time()
        cls.START_TIME = cls.ENGINE_START_TIME
        cls.update_time()

    @classmethod
    def update_time(cls):
        """Updates time."""
        cls.END_TIME = time.time()
        cls.DELTA = cls.END_TIME - cls.START_TIME
        cls.START_TIME = cls.END_TIME
        cls.ENGINE_UPTIME += cls.DELTA
        # update all clocks
        cls.update_global_clocks()
    
    @classmethod
    def pause_time(cls, t: float):
        """Pauses time for a certain amount of time."""
        time.sleep(t)

    @classmethod
    def get_current_time(cls):
        """Returns the current system time"""
        return cls.START_TIME
    
    # ------------------------------ #
    # global clock queue
    ALL_CLOCKS = {}
    ACTIVE_CLOCKS = set()
    REMOVE_ARR = set()

    @classmethod
    def deactivate_timer(cls, timer):
        """Deactivate a timer"""
        cls.REMOVE_ARR.add(timer.hash)
    
    @classmethod
    def activate_timer(cls, timer):
        """Activate a timer"""
        cls.ACTIVE_CLOCKS.add(timer.hash)
    
    @classmethod
    def get_timer(cls, limit: float=0, loop: bool=False):
        """Get a timer object"""
        c = SoraContext.Timer(limit, loop)
        cls.ALL_CLOCKS[c.hash] = c
        cls.activate_timer(c)
        return c
    
    @classmethod
    def update_global_clocks(cls):
        """Update all active clocks"""
        for c in cls.ACTIVE_CLOCKS:
            cls.ALL_CLOCKS[c].update()
        for c in cls.REMOVE_ARR:
            cls.ACTIVE_CLOCKS.remove(c)
        cls.REMOVE_ARR.clear()

    # ------------------------------ #
    # timer class

    class Timer:
        def __init__(self, limit:float, loop:bool):
            self.hash = hash(self)
            self.initial = SoraContext.get_current_time()
            self.passed = 0
            self.loopcount = 0
            self.limit = limit
            self.loop = loop

        def update(self):
            """Updates the clock - throws a signal when finished"""
            self.passed += SoraContext.DELTA
            # to implement sending signals -- when completed!
            # print(self.passed)
            if self.passed > self.limit:
                # -- emit a signal
                self.passed = 0
                self.loopcount += 1
                if not self.loop:
                    SoraContext.deactivate_timer(self)
        
        def reset_timer(self, time:float=0):
            """Reset the timer"""
            self.initial = SoraContext.get_current_time()
            self.passed = 0
            self.loopcount = 0

    # ------------------------------ #
    # window variables

    FPS = 60
    WSIZE = [1280, 720]
    WPREVSIZE = [1280, 720]
    WFLAGS = pygame.RESIZABLE | pygame.DOUBLEBUF
    WBITS = 32
    FFLAGS = pygame.SRCALPHA
    FPREVSIZE = [1280, 720]
    FSIZE = [1280, 720]
    FBITS = 32

    MODERNGL = False

    # setup engine
    @classmethod
    def initialize(cls, options: dict = {}):
        """Initialize Sora Engine with options."""
        cls.FPS = options["fps"] if "fps" in options else 60
        cls.WSIZE = options["window_size"] if "window_size" in options else [1280, 720]
        cls.WFLAGS = options["window_flags"] if "window_flags" in options else pygame.RESIZABLE | pygame.DOUBLEBUF
        cls.WBITS = options["window_bits"] if "window_bits" in options else 32
        cls.FFLAGS = options["framebuffer_flags"] if "framebuffer_flags" in options else pygame.SRCALPHA
        cls.FSIZE = options["framebuffer_size"] if "framebuffer_size" in options else cls.WSIZE
        cls.FBITS = options["framebuffer_bits"] if "framebuffer_bits" in options else 32
        cls.DEBUG = options["debug"] if "debug" in options else False
        # add options as required!
        cls.MODERNGL = cls.is_flag_active(pygame.OPENGL)
        if cls.MODERNGL:
            from . import mgl
        return cls

    # check if certain flags are active
    @classmethod
    def is_flag_active(cls, flag: int):
        """Checks if a flag is active."""
        return bool(cls.WFLAGS & flag)

    # ------------------------------ #
    # window/camera data
    WINDOW = None
    FRAMEBUFFER = None
    DEBUGBUFFER = None
    CLOCK = None
    RUNNING = False
    
    @classmethod
    def create_context(cls):
        """Creates window context and Framebuffer for Sora Engine."""
        cls.WINDOW = pygame.display.set_mode(cls.WSIZE, cls.WFLAGS, cls.WBITS)
        cls.FRAMEBUFFER = pygame.Surface(cls.FSIZE, cls.FFLAGS, cls.FBITS)
        cls.DEBUGBUFFER = pygame.Surface(cls.FSIZE, cls.FFLAGS | pygame.SRCALPHA, cls.FBITS)
        cls.CLOCK = pygame.time.Clock()
        cls.RUNNING = True
    
    @classmethod
    def push_framebuffer(cls):
        """Pushes framebuffer to window."""
        if cls.MODERNGL:
            # push frame buffer to moderngl window context
            mgl.ModernGL.render(mgl.Texture.pg2gltex(cls.FRAMEBUFFER, "fb"))
            if cls.DEBUG:
                mgl.ModernGL.render(mgl.Texture.pg2gltex(cls.DEBUGBUFFER, "debug"))
            pygame.display.flip()
        else:
            # render frame buffer texture to window!
            cls.WINDOW.blit(pygame.transform.scale(cls.FRAMEBUFFER, cls.WSIZE), (0,0))
            cls.WINDOW.blit(pygame.transform.scale(cls.DEBUGBUFFER, cls.WSIZE), (0,0))
            pygame.display.update()

    @classmethod
    def refresh_buffers(cls, color):
        """Refreshes framebuffer and debugbuffer"""
        cls.FRAMEBUFFER.fill(color)
        cls.DEBUGBUFFER.fill((0, 0, 0, 0))

    @classmethod
    def update_window_resize(cls, event):
        """Updates window size and framebuffer size."""
        cls.WPREVSIZE[0], cls.WPREVSIZE[1] = cls.WSIZE[0], cls.WSIZE[1]
        cls.WSIZE[0], cls.WSIZE[1] = event.x, event.y

    # TODO - changing fb res
    
    # ------------------------------ #
    # hardware data -- input [mouse]
    MOUSE_POS = [0, 0]
    MOUSE_MOVE = [0, 0]
    MOUSE_BUTTONS = [False, False, False]
    MOUSE_PRESSED = set()
    MOUSE_SCROLL = [0, 0]
    MOUSE_SCROLL_POS = [0, 0]

    @classmethod
    def update_mouse_pos(cls, event):
        """Update mouse position."""
        cls.MOUSE_MOVE[0], cls.MOUSE_MOVE[1] = event.rel
        cls.MOUSE_POS[0], cls.MOUSE_POS[1] = event.pos

    @classmethod
    def update_mouse_press(cls, event):
        """Update mouse button press."""
        cls.MOUSE_BUTTONS[event.button - 1] = True
        cls.MOUSE_PRESSED.add(event.button - 1)

    @classmethod
    def update_mouse_release(cls, event):
        """Update mouse button release."""
        cls.MOUSE_BUTTONS[event.button - 1] = False
    
    @classmethod
    def update_mouse_scroll(cls, event):
        """Update mouse scroll."""
        cls.MOUSE_SCROLL[0], cls.MOUSE_SCROLL[1] = event.rel
        cls.MOUSE_SCROLL_POS[0], cls.MOUSE_SCROLL_POS[1] = event.pos
    
    # ------------------------------ #
    # hardware data -- input [keyboard]
    KEYBOARD_KEYS = {}
    KEYBOARD_PRESSED = set()

    # ensure that the error does not occur
    for i in range(0, 3000):
        KEYBOARD_KEYS[i] = False
    
    @classmethod
    def update_keyboard_down(cls, event):
        """Update keyboard key press."""
        cls.KEYBOARD_KEYS[event.key] = True
        cls.KEYBOARD_PRESSED.add(event.key)
    
    @classmethod
    def update_keyboard_up(cls, event):
        """Update keyboard key release."""
        cls.KEYBOARD_KEYS[event.key] = False
    
    # ------------------------------ #
    # hardware data -- input [key + mouse]

    @classmethod
    def update_hardware(cls):
        """Updates the mouse"""
        # print("DEBUG:", cls.MOUSE_PRESSED, cls.KEYBOARD_PRESSED)
        cls.MOUSE_PRESSED.clear()
        cls.MOUSE_SCROLL = [0, 0]
        cls.KEYBOARD_PRESSED.clear()
    
    @classmethod
    def get_mouse_rel(cls):
        """Returns mouse position."""
        return (cls.MOUSE_POS[0] / cls.WSIZE[0] * cls.FSIZE[0], cls.MOUSE_POS[1] / cls.WSIZE[1] * cls.FSIZE[1])

    @classmethod
    def get_mouse_abs(cls):
        """Returns mouse position."""
        return (cls.MOUSE_POS[0], cls.MOUSE_POS[1])
    
    @classmethod
    def is_mouse_pressed(cls, button):
        """Returns if mouse button is pressed."""
        return cls.MOUSE_BUTTONS[button]

    @classmethod
    def is_mouse_clicked(cls, button):
        """Returns if mouse button is clicked."""
        return button in cls.MOUSE_PRESSED
    
    @classmethod
    def is_key_pressed(cls, key):
        """Returns if key is pressed."""
        return cls.KEYBOARD_KEYS[key]

    @classmethod
    def is_key_clicked(cls, key):
        """Returns if key is clicked."""
        return key in cls.KEYBOARD_PRESSED

    @classmethod
    def handle_pygame_events(cls):
        """Handles pygame events."""
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                cls.RUNNING = False
            elif e.type == pygame.KEYDOWN:
                # keyboard press
                cls.update_keyboard_down(e)
            elif e.type == pygame.KEYUP:
                # keyboard release
                cls.update_keyboard_up(e)
            elif e.type == pygame.MOUSEMOTION:
                # mouse movement
                cls.update_mouse_pos(e)
            elif e.type == pygame.MOUSEWHEEL:
                # mouse scroll
                cls.update_mouse_scroll(e)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                # mouse press
                cls.update_mouse_press(e)
            elif e.type == pygame.MOUSEBUTTONUP:
                # mouse release
                cls.update_mouse_release(e)
            elif e.type == pygame.WINDOWRESIZED:
                # window resized
                cls.update_window_resize(e)

    # ------------------------------ #
    # filehandler
    IMAGES = {}
    CHANNELS = {}
    AUDIO = {}
    FONTS = {}

    @classmethod
    def load_image(cls, path):
        """Loads image from file."""
        if path in cls.IMAGES:
            return cls.IMAGES[path]
        cls.IMAGES[path] = pygame.image.load(path).convert_alpha()
        return cls.IMAGES[path]

    @classmethod
    def scale_image(cls, image, size):
        """Scales image to size."""
        return pygame.transform.scale(image, size)
    
    @classmethod
    def load_and_scale(cls, image, size):
        """Loads and scales image to size."""
        return cls.scale_image(cls.load_image(image), size)

    @classmethod
    def make_channel(cls, name):
        """Creates a new channel."""
        cls.CHANNELS[name] = pygame.mixer.Channel(len(cls.CHANNELS))

    @classmethod
    def load_audio(cls, path):
        """Loads audio from file."""
        if path in cls.AUDIO:
            return cls.AUDIO[path]
        cls.AUDIO[path] = pygame.mixer.Sound(path)
        return cls.AUDIO[path]

    @classmethod
    def play_audio(cls, path, channel):
        """Plays audio on channel."""
        cls.CHANNELS[channel].play(cls.load_audio(path))
    
    @classmethod
    def play_music(cls, path):
        """Plays music."""
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)
    
    @classmethod
    def stop_music(cls):
        """Stops music."""
        pygame.mixer.music.stop()
    
    @classmethod
    def set_volume(cls, volume):
        """Sets volume."""
        pygame.mixer.music.set_volume(volume)

    @classmethod
    def load_font(cls, path, size):
        """Loads font from file."""
        fs = f"{path}|{size}"
        if fs in cls.FONTS:
            return cls.FONTS[fs]
        cls.FONTS[fs] = pygame.font.Font(path, size)
        return cls.FONTS[fs]
