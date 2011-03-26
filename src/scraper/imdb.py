import logging
import lxml.html
import csv
from download import download
from ThreadDistributor import ThreadDistributor, Task

N_THREADS = 10


class ReviewScrapeTask(Task):
    """Scrape reviews from a movie
    
    """
    URL = "http://www.imdb.com%(link)susercomments?start=%(start)d"
    REVIEWS_PER_PAGE = 10
    START = 0
    fo = csv.writer(open("imdb/reviews.tsv", "w"), delimiter="\t", quotechar="\"")
    
    def run(self):
        link, start, title = self.inp["link"], self.inp["start"], self.inp["title"]
        url = self.URL % self.inp
        content = download(url)
        # logging.info("Downloading %r" % url)
        if content is None: 
            # logging.debug("Can't download %r" % url)
            return
            
        dom = lxml.html.fromstring(content)
        review_titles = dom.xpath("//hr/following-sibling::p[1]/b[1]/text()")
        rates = dom.xpath("//hr/following-sibling::p[1]/img/attribute::alt")
        contents = map(\
            lambda p: p.text_content().replace("\n", "\\n"), \
            dom.xpath("//div[@class='yn']/preceding-sibling::p[1]")\
        )
        map(lambda row: self.fo.writerow(\
                map(lambda text: text.encode("utf-8"), row)\
                ),
            zip([link]*len(rates) , [title]*len(rates), rates, review_titles, contents))
            
        self.distributor.add_task(ReviewScrapeTask, {
            "link"  : link, 
            "title" : title,
            "start" : start + self.REVIEWS_PER_PAGE
        })
        
        yield None
        


class MovieScrapeTask(Task):
    """Scrape movie titles and their links
    
    """
    URL = "http://www.imdb.com/search/title?sort=user_rating,asc&start=%(start)d&title_type=feature"
    MOVIES_PER_PAGE = 50
    START = 1
    
    def run(self):
        start = self.inp
        url = self.URL % {"start": start}
        # logging.info("Downloading %s" % url)
        content = download(url)
        if content is None: 
            # logging.debug("Can't download: %r" % url)
            self.distributor.stop()
            return

        dom = lxml.html.fromstring(content)
        links = dom.xpath("//td[@class='title']/a")
        if len(links) == 0:
            self.distributor.stop()
            return
            
        for link in links:
            title = link.text
            relative_url = link.get("href")
            # logging.info(title, relative_url)
            self.distributor.add_task(ReviewScrapeTask, {
                "link"  : relative_url,
                "title" : title,
                "start" : ReviewScrapeTask.START
            })
            
        self.distributor.add_task(MovieScrapeTask, start + self.MOVIES_PER_PAGE)
            
        yield None


if __name__ == "__main__":
    logging.basicConfig(\
        level = logging.DEBUG, \
        filename="imdb/log.txt", \
        filemode="w", \
        format="%(asctime)s\t%(levelname)s\t(%(threadName)-10s)\t%(message)s"\
    )
    distributor = ThreadDistributor(N_THREADS)
    distributor.add_task(MovieScrapeTask, MovieScrapeTask.START)
    distributor.run()
    
