# from engine import animation, misc
# import json

# # animation.Category.load_category("assets/sprites/tomato.json")
# # r = animation.Category.get_category_framedata("assets/sprites/tomato.json")

# # print(r)

import os

nn = "assets/sprites/tomato.json"

print(os.path.relpath(nn))
os.path.abspath(nn)


