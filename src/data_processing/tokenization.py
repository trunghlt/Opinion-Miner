import re

class Tokenizer:

    std_regex = re.compile(r"[a-zA-Z0-9]{2,}")

    def __init__(self, text):
        self.text = text
        
    def standard(self):
        return self.std_regex.findAll(self.text)
