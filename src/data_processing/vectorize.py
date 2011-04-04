import numpy as np
import math
import csv
import random
import re

#stopWordList = stopwords.raw("english")
STD_REGEX = re.compile("[a-zA-Z0-9]{2,}")

class Vectorizer():
    regex = STD_REGEX

    def __init__(self, desc, corpus, cat, ngram=3, limit=None, nclasses=5, \
                       tail="", lower = True, regex = STD_REGEX):
        self.desc = desc
        self.dir = cat                       
        self.cat = cat
        self.corpus = corpus
        self.ngram = ngram
        self.limit = limit
        self.lower = lower
        self.nclasses = nclasses
        self.regex = regex
        
        self.count = [0]*(nclasses + 1)
        self.training_count = [0]*(nclasses + 1)
        self.testing_count = [0]*(nclasses + 1)
        
        self.basename = "%s/%s/%s.%d-gram%s" % (corpus, cat, cat, ngram, tail)
        self.ftrain = open(self.basename, "w")
        self.ftest = open(self.basename + ".test", "w")
        self.findex = open(self.basename + ".index", "w")
        self.training_features = {}
        self.index_max = 0
        self.index = {}
        self.nfeatures = 0
        
        
    @classmethod
    def get_ngrams(cls, review, ngram=1, with_pos=False, union=True):
        tokens = []
        for t in cls.regex.finditer(review.lower()):
            tokens.append(t)
            
        starts, ends, features = [], [], []
        for i in xrange(len(tokens)):
            for j in xrange(ngram):
                if i + j < len(tokens):
                    f = " ".join(map(lambda t: t.group(0), tokens[i:i+j+1]))
                    if not union or not f in features:
                        features.append(f)
                        starts.append(tokens[i].start())
                        ends.append(tokens[i+j].end())
                    
        return features, starts, ends if with_pos else features
        

    def run(self, inpYielder):
        for score, text in inpYielder():
            # lowercase if set
            if self.lower: text = text.lower()            
            
            tokens = re.findall(self.regex, text.lower())

            features = self.get_ngrams(text, self.ngram)
            for f in filter(lambda f: not self.index.has_key(f), features):
                self.add_to_index(f)
            
            id_feature_pairs = sorted(map(lambda f: (self.index[f], f), features))
            
            output = "%d %s" % (\
                score, \
                " ".join(map(lambda p: str(p[0])+":1", id_feature_pairs))\
            )
            
            self.count[score] += 1
            
            if self.limit is None or self.count[score] < self.limit:
                self.training_count[score] += 1
                for t in id_feature_pairs:
                    if not self.training_features.has_key(t[1]):
                        self.training_features[t[1]] = t[0]
                        
                self.ftrain.write(output + "\n")
            else:
                self.testing_count[c] += 1
                self.ftest.write(output + "\n")
            
        self.ftrain.close()
        self.ftest.close()
        self.findex.close()
        self.report()
            
                        
    def add_to_index(self, f):
        self.index_max += 1
        self.index[f] = self.index_max
        self.findex.write("%d\t%s\n" % (self.index_max, f))
        
        
    def report(self):
        self.readme = open(self.basename + ".info", "w")
        self.readme.write(self.desc + "\n")
        self.readme.write("------------------------------------\n")
        self.readme.write("Number of vectors: %d\n" % sum(self.count))
        self.readme.write("Number of training vectors: %d\n" % sum(self.training_count))
        self.readme.write("Number of testing vectors: %d\n" % sum(self.testing_count))
        self.readme.write("Total number of features: %d\n" % self.index_max)
        self.readme.write("Total number of training features: %d\n" % len(self.training_features))
        self.readme.close()
    
if __name__ == "__main__":
    generator = Vectorizer("Amazon/dvd/amazon_reviews_dvd.txt",\
                           "Amazon",\
                           "dvd", 3,\
                           limit=1000,\
                           tail=".limit_1000")
    generator.generate()
