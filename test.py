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
        self.data = {}
    def __hash__(self):
        return hash(self.val)
    def __setitem__(self, name, value):
        self.data[name] = value
    def __getitem__(self, name):
        return self.data[name]


a = X(1)
b = X(2)

print(hash(a))
print(hash(b))

arr = {}
arr[a] = a
arr[b] = b

print(arr)

a['a'] = 0
print(a['a'])


