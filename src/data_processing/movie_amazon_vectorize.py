import os.path
from csv import reader
from vectorize import Vectorizer

PATH = "../../data/movie/amazon"

def score_review_pairs():
    fi = reader(
        open(os.path.join(PATH, "processed_reviews.tsv"), "r"),
        delimiter="\t",
        quotechar="\""
    )
    for score, review in fi:
        yield int(score), review
        
vectorizer = Vectorizer(
    "Amazon dvd",
    "Movie", 
    "amazon", 
    ngram=3,
)

vectorizer.run(score_review_pairs)
