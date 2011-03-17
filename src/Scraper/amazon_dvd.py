import logging
import re
import urllib2
import demjson
import lxml.html 
import time
from dateutil.parser import parse
from semetric.util.scraper import ScraperLogMessage, Scraper, ScraperDownloadError

class AmazonFutureReleaseScraper():
        
    #URL="http://www.amazon.co.uk/mn/search/ajax/ref=sr_pg_3_ajx_0?rh=n:229816,p_69:30x-7y,p_n_date:182239031&page=%(page)d&bbn=229816&sort=-releasedate&ie=UTF8&qid=1296143906&tab=music&pageTypeID=229816&fromHash=undefined&fromRH=n:229816,p_69:30x-7y&section=ATF,BTF&version=2&rrid=16HJ0F353VJJ0NQKNFYD"
    URL="http://www.amazon.co.uk/mn/search/ajax/ref=sr_pg_2?rh=n%%3A283926&page=%(page)d&sort=reviewrank&ie=UTF8&qid=1300376652&tab=dvd&pageTypeID=283926&fromHash=undefined&fromRH=n%%3A283926&section=ATF,BTF&fromApp=gp%%2Fsearch&fromPage=results&version=2&rrid=1YF9C2Y1ZRP1E82X11MH"

    def __init__(self):
        self.page = 1
        pass
        
    def get(self):
        self.results = []
        self.page = 1
        while True:
            for message in self.get_page(self.page): 
                if message is None: 
                    yield ScraperLogMessage("Completed !", logging.DEBUG)
                    return
                yield message
            self.page += 1
        
    def get_page(self, page):
        yield ScraperLogMessage("Downloading page %s" % page, logging.DEBUG)
        url = self.URL % {"page": page}
        try:
            jsonStr = "[" + urllib2.urlopen(url).read().replace("&&&", ",") + "]"
        except Exception, e:
            print e
        
        """
        try:
            yield ScraperLogMessage("Downloading page %s" % page, logging.DEBUG)
            url = self.URL % {"page": page}
            jsonStr = u"[" + urllib2.urlopen(url).read().replace(u"&&&", u",") + u"]"
        except:
            yield None
        """
        try:
            data = demjson.decode(jsonStr, encoding="latin-1")
        except Exception, e:
            print e

        """
        try:
            data = demjson.decode(jsonStr, encoding="latin-1")
        except demjson.JSONDecodeError:
            yield ScraperLogMessage("Parsing error!!!", logging.DEBUG)
            yield None
        """
            
        found = False
        for key in ["results-atf", "results-btf"]:
            for chunk in data:
                if chunk.has_key(key):
                    try:    doms = lxml.html.fromstring(chunk[key]["data"]["value"])
                    except: continue
                    
                    for e in doms.cssselect(".result"): 

                        found = True
                    
                        try:    releaseId = e.get("name").split("_")[0]
                        except: releaseId = "Unknown"
                    
                        try:    release = e.cssselect("a.title")[0].text
                        except: release = "Unkown"
                        
                        try:    artist = e.cssselect(".ptBrand")[0].text_content()[3:]
                        except: artist = "Unknown"
                            
                        try:
                            fastTrack = e.cssselect(".fastTrack")[0].text
                            m = re.search(r"[0-9]+\s[a-zA-Z]{,10}\s[0-9]+", fastTrack)
                            date = int(time.mktime(parse(m.group(0)).timetuple()))
                        except:
                            date = "Unknown"
                                
                        yield ScraperLogMessage([artist, release, releaseId, date], logging.INFO)
                        self.results.append([artist, release, releaseId, date])
                        
        if not found: yield None
        
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG, format="%(asctime)s\t%(levelname)s\t%(message)s")
    scraper = AmazonFutureReleaseScraper()
    for message in scraper.get():
        logging.log(message.level, message.message)
    print scraper.results
