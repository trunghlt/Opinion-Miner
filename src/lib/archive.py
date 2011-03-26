import os

class Archive:

    def __init__(self, path):
        self.path = path
        
    def save(self, content, filename):
        f = open(os.path.join(self.path, filename), "w")
        f.write(content)
        f.close()
