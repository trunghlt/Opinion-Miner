import logging
import lxml.html
from download import download
from thread_distributor import ThreadDistributor, Task
import MySQLdb
from credential import DB
from datetime import datetime
import urllib

db = MySQLdb.connect(DB["host"], DB["user"], DB["passwd"], DB["name"])


class DetailScrapeTask(Task):

    def run(self):
        url, imdb_id = "http://www.imdb.com" + self.inp["url"], self.inp["imdb_id"]
        id = self.inp["id"]
        dom = lxml.html.fromstring(download(url))
        metadata = dict(map(
            lambda h4: (
                h4.text.strip().split(":")[0], 
                reduce(
                    lambda x, y: x + y, 
                    map(
                        lambda a: lxml.html.tostring(a) if isinstance(a, lxml.html.HtmlElement) else a, 
                        h4.xpath("following-sibling::node()")
                    )
                )
            ),
            dom.xpath("//td[@id='overview-top']//h4[@class='inline']")   
        ))
        metadata["infobar"] = lxml.html.tostring(dom.xpath("//div[@class='infobar']")[0])
        cursor = db.cursor()
        for k, v in metadata.items():
            cursor.execute("INSERT INTO metadata(movie_id, `key`, value) VALUES (%s, %s, %s)",
                           (str(id), k, v))
        
        yield None
                

class NowPlayingScrapeTask(Task):
    def run(self):
        url = self.inp
        dom = lxml.html.fromstring(download(url))
        image_urls = dom.xpath("//img[@class='poster']/attribute::src")
        names = dom.xpath("//a[@class='title']/text()")
        urls = dom.xpath("//a[@class='title']/attribute::href")
        plots = dom.xpath("//span[text()='The Plot:']/following::node()[1]")
        image = urllib.URLopener()

        for name, url, image_url, plot in zip(names, urls, image_urls, plots):
            cursor = db.cursor()
            imdb_id = url.split("/")[-2]
            image.retrieve(image_url, "../www/static/images/%s.png" % imdb_id)
            cursor.execute("INSERT IGNORE INTO movies (imdb_id, name, image_url,  plot, created_time)"
                           "VALUES (%s, %s, %s, %s, %s)",
                           (imdb_id, name, image_url, plot,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S") ))

            if cursor.lastrowid != 0:                              
                self.distributor.add_task(
                    DetailScrapeTask, 
                    {"url": url, "imdb_id": imdb_id, "id": cursor.lastrowid}
                )
        
        yield None


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG, 
        filename="logs/imdb_nowplaying.log", 
        filemode="w", 
        format="%(asctime)s\t%(levelname)s\t%(threadName)s\t%(message)s"
    )
    distributor = ThreadDistributor(1)
    distributor.add_task(NowPlayingScrapeTask, "http://www.imdb.com/nowplaying/")
    distributor.run()
