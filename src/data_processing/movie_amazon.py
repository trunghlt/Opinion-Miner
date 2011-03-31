#!/usr/bin/env python
#
# Copyright 2011 Trung Huynh
#
# Licnesed under GNU GPL, Version 3.0 (the "License"); you may not use this 
# file except in compliance with the License. You may obtain a copy of the 
# License at
#
#     http://www.gnu.org/licenses/gpl.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import csv
from amazon import Movie
from utils import erase

PATH = "../../data/movie/amazon"

fi = csv.reader(
    open(os.path.join(PATH, "reviews.csv"), "r"), 
    delimiter="\t", 
    quotechar="\""
)

fo = csv.writer(
    open(os.path.join(PATH, "processed_reviews.tsv"), "w"),
    delimiter="\t",
    quotechar="\""
)

for score, product_title, review_title, review_content in fi:
    movie_title = Movie.extract_title(product_title)
    review_title = erase(movie_title, review_title)
    review_content = erase(movie_title, review_content)
    fo.writerow([score, review_title + ". " + review_content])
    
