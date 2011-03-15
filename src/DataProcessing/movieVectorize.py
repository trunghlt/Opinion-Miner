import os
from vectorize import Vectorizer

DATA_DIR = "../../data/movie/polarity_dataset_v1.0/tokens"

def inpYielder():
    root = DATA_DIR
    neg_dir = os.path.join(root, "neg")
    for fileName in os.listdir(neg_dir):
        print fileName
        f = open(os.path.join(neg_dir, fileName), "r")
        yield 0, f.read()
        f.close()
        
    pos_dir = os.path.join(root, "pos")
    for fileName in os.listdir(pos_dir):
        print fileName
        f = open(os.path.join(pos_dir, fileName), "r")
        yield 1, f.read()
        f.close()
    
vectorizer = Vectorizer(\
    "Bo Pang's movie data", \
    "Movie", \
    "polarity_dataset_v1.0", \
    ngram = 1,\
)

vectorizer.run(inpYielder)
