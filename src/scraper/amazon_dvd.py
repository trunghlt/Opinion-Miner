"""Scrape Amazon DVD reviews

Author  : Trung Huynh
Ver     : 0.1

"""

import os
import csv
import logging
import re
import urllib2
import demjson
import lxml.html 
import time
from dateutil.parser import parse
from ThreadDistributor import ThreadDistributor, Task

# Disabled archiving
ARCHIVE_ENABLED = False
SEARCH_START_PAGE = 1
OUTPUT_MODE = "w"

def download(url, max_retries=5):    
    """Content downloaded from ``url``, maximum retry number is set by 
    ``max_retries``.
        
    """
    for i in xrange(max_retries):
        try:
            return urllib2.urlopen(url).read()
        except Exception, e:
            print "Retries: %d, url: %s" % (i + 1, url)
            pass
    return None
    

class Archive:
    """Archive content to different files in a specific folder.
    
    """    
    def __init__(self, path, enabled=ARCHIVE_ENABLED):
        self.path = path
        self.enabled = enabled
        
    def save(self, content, filename):        
        if self.enabled:
            f = open(os.path.join(self.path, filename), "w")
            f.write(content)
            f.close()


class ReviewScrapeTask(Task):
    """Scrape reviews in a page of a DVD product.
    
    Input is a dictionary with format of {"code": product code, "page": page
    number for downloading}.
    
    """

    URL = "http://www.amazon.co.uk/Firefly-Complete-DVD-Region-NTSC/product-reviews/%(code)s/ref=sr_1_1_cm_cr_acr_txt?ie=UTF8&showViewpoints=1&pageNumber=%(page)d"
    archive = Archive("Amazon/DVD/reviews")
    output = csv.writer(\
        open("Amazon/DVD/reviews.csv", OUTPUT_MODE), \
        delimiter="\t", \
        quotechar="\""\
    )
    
    def run(self):
        code, page, name = self.inp["code"], self.inp["page"], self.inp["name"]
        html = download(self.URL % {"code": code, "page": page})
        if html is None: return
        
        ReviewScrapeTask.archive.save(html, "%s_%d.html" % (code, page))
        dom = lxml.html.fromstring(html)
        
        try: productReviews = dom.get_element_by_id("productReviews")
        except KeyError: return 

        self.distributor.add_task(ReviewScrapeTask, {
            "name": name, 
            "code": code, 
            "page": page + 1 
        }) 

        for div in productReviews.cssselect("td > div"):
            try:
                rate = int(div.cssselect(".swSprite")[0].get("title")[0])
            except Exception, e:
                rate = -1
                
            try:
                title = div.cssselect("b")[0].text or ""
            except Exception, e:
                title = ""
            
            content = ""
            for e in div:
                if e.tag == "p": content += e.text or ""
                content += e.tail or ""
                
            logging.info("REVIEW dvd: %s, rate: %d, title: %s, content: %s"\
                         % (name, rate, title, content.strip()))
                         
            self.output.writerow([
                rate,
                name.encode("utf-8"), 
                title.encode("utf-8"), 
                content.strip().encode("utf-8")
                ])
        
        yield None       


class SearchTask(Task):
        
    URL="http://www.amazon.co.uk/mn/search/ajax/ref=sr_pg_2?rh=n%%3A283926&page=%(page)d&sort=reviewrank&ie=UTF8&qid=1300376652&tab=dvd&pageTypeID=283926&fromHash=undefined&fromRH=n%%3A283926&section=ATF,BTF&fromApp=gp%%2Fsearch&fromPage=results&version=2&rrid=1YF9C2Y1ZRP1E82X11MH"
    archive = Archive("Amazon/DVD/searchs")
    
    def run(self):
        page = self.inp
        content = download(self.URL % {"page": page})
        if content is None: return
        
        SearchTask.archive.save(content, "%d.html" % page)
        jsonStr = "[%s]" % content.replace("&&&", ",")
        data = demjson.decode(jsonStr, encoding="latin-1")
        found = False
        for key in ["results-atf", "results-btf"]:
            for chunk in data:
                if chunk.has_key(key):
                    try:    doms = lxml.html.fromstring(chunk[key]["data"]["value"])
                    except: continue
                    
                    for e in doms.cssselect(".result"): 
                        found = True
                    
                        try:    code = e.get("name").split("_")[0] or ""
                        except: code = ""
                    
                        try:    name = e.cssselect("a.title")[0].text or ""
                        except: name = ""
                        
                        self.distributor.add_task(ReviewScrapeTask, {
                            "name": name, 
                            "code": code, 
                            "page": 1 
                        }) 
                        logging.info("SEARCH dvd: %s, code: %s, page: %d" \
                                     % (name, code, page))
                        
        if found: self.distributor.add_task(SearchTask, page + 1)
        yield None
    
if __name__ == "__main__":
    logging.basicConfig(\
        level = logging.DEBUG, \
        filename="Amazon/DVD/log.txt", \
        filemode="w", \
        format="%(asctime)s\t%(levelname)s\t%(threadName)s\t%(message)s"\
    )
    distributor = ThreadDistributor(20)
    distributor.add_task(SearchTask, SEARCH_START_PAGE)
    distributor.run()
