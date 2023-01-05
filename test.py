# from engine import animation, misc
# import json

# # animation.Category.load_category("assets/sprites/tomato.json")
# # r = animation.Category.get_category_framedata("assets/sprites/tomato.json")

# # print(r)

# import os

# nn = "assets/sprites/tomato.json"

# print(os.path.relpath(nn))
# os.path.abspath(nn)

class X:
    def __init__(self, val):
        self.val = val
    def __hash__(self):
        return hash(self.val)


a = X(1)
b = X(2)

print(hash(a))
print(hash(b))

arr = {}
arr[a] = a
arr[b] = b

print(arr)
