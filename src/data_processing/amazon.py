#!/usr/bin/env python
#
# Copyright 2011 Trung Huynh
#
# Licnesed under GNU GPL, Version 3.0; you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.gnu.org/licenses/gpl.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A util module for text processing for Amazon data

"""        
import re

class Movie:
    COMMENT_REGEX = re.compile("\(.*\)|\[.*\]")
    PRODUCT_TITLE_SEP = re.compile("[-:]")

    @staticmethod
    def extract_title(product_title):
        """Extract real movie title from product title
        
        ``product_title``: product title, usually is found while crawling 
        Amazon website, e.g. "Up Superset (2 Blu-ray Discs + 1 DVD Disc + 1
        Digital Copy Disc) [2009]".
        
        Return movie title, e.g. Up Superset
        
        """
        # Firefly: Complete Series (3pc) (Ws Dub Sub Ac3) [Blu-ray] [US Import]
        # Up Superset (2 Blu-ray Discs + 1 DVD Disc + 1 Digital Copy Disc) [2009]
        # Band Of Brothers - Complete HBO Series Commemorative Gift Set (6 Disc Box Set) [2001] [DVD]
        # The Shawshank Redemption [DVD] [1995]
        
        # => remove all text in (), [], get the first part of splits by "-", ":"
        s = Movie.COMMENT_REGEX.sub("", product_title)
        return Movie.PRODUCT_TITLE_SEP.split(s)[0].strip()
