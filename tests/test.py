import soragl
from soragl import physics

import pygame
import random
from pygame.math import Vector2

from queue import deque
from soragl import smath


points = []
for i in range(30):
    points.append(Vector2(random.randint(200, 1000), random.randint(200, 600)))



# setup
SORA = soragl.SoraContext.initialize()
SORA.create_context()


# calculations
hull = []

points.sort(key=lambda p: (p.x, p.y))
pmin, pmax = points[0], points[-1]
line = smath.Linear.get_from_points(pmin, pmax)
hull += [pmin, pmax]

s1, s2 = [], []
for p in points:
    # determine if left or right of line
    s1.append(p) if line.above(p) else s2.append(p)


INSIDE = []

# recursion
def findhull(sk, p, q, top = True):
    # find points on convex hull from set sk of points
    if not sk:
        return
    # search furthest point from line
    c = line.furthest_point(sk)
    tline = smath.Linear.get_from_points(p, c)
    hull.append(c)
    # partition rest of points into 3 sections
    s0, s1, s2 = [], [], []
    # s0 = inside triangle
    # s1 = left of p->c
    # s2 = right of c->q
    l1 = smath.Linear.get_from_points(p, c)
    l2 = smath.Linear.get_from_points(c, q)
    # print(l1, l2)
    # how to determine if left or right???
    for p in sk:
        if not top:
            if l1.below(p):
                s1.append(p)
            elif l2.below(p):
                s2.append(p)
            else:
                s0.append(p)
        else:
            if l1.above(p):
                s1.append(p)
            elif l2.above(p):
                s2.append(p)
            else:
                s0.append(p)
    # log
    print(s1, s2)

    # recurse
    findhull(s1, p, tline.highest_point(sk), not top)
    findhull(s2, tline.lowest_point(sk), q, top)

"""
TODO:
1. swap from finding abs y dif --> switch to using perp rel distance!
    - separate the binary searching alrogith into 2 sections, top and bottom
    - each search will separate into left + right

"""

# recurse
findhull(s1, pmin, pmax)
findhull(s2, pmax, pmin, False)

# fix the points
# start with points above line
above = []
below = []
for p in hull:
    if line.above(p):
        above.append(p)
    else:
        below.append(p)
above.sort(key=lambda p: (p.x))
below.sort(key=lambda p: (-p.x))
hull = above + below


def draw_points(points, color):
    for p in points:
        pygame.draw.circle(SORA.FRAMEBUFFER, color, p, 5)

BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

SORA.start_engine_time()
while SORA.RUNNING:
    SORA.FRAMEBUFFER.fill((0, 0, 0, 255))
    # pygame update + render

    pygame.draw.rect(SORA.FRAMEBUFFER, (255, 255, 255), (200, 200, 800, 400), 2)
    draw_points(points, (255, 255, 255))

    # draw hull
    if len(hull) > 1:
        pygame.draw.polygon(SORA.FRAMEBUFFER, BLUE, hull, 1)

    # draw intersect
    pygame.draw.line(SORA.FRAMEBUFFER, RED, pmin, pmax, 1)
    
    # other data
    draw_points(INSIDE, GREEN)
    draw_points(hull, RED)


    if SORA.is_key_clicked(pygame.K_SPACE):
        perform_single_check()

    # engine update
    SORA.push_framebuffer()
    SORA.update_hardware()
    SORA.handle_pygame_events()
    # clock
    SORA.CLOCK.tick(SORA.FPS)
    SORA.update_time()





