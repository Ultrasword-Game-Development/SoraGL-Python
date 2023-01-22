"""
Misc functions:
- io
- idk

"""

def fread(path):
    """Read a file and return its content as a string"""
    with open(path, 'r') as f:
        return f.read()

def fwrite(path, data: str):
    """Write a string to a file"""
    with open(path, 'w') as f:
        f.write(data)



