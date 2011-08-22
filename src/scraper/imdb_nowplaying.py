import logging
import lxml.html
from download import download
from thread_distributor import ThreadDistributor, Task
import MySQLdb
from credential import DB
import time

db = MySQLdb.connect(DB["host"], DB["name"], DB["user"], DB["passwd"])


class DetailScrapeTask(Task):

    def run(self):
        url, imdb_id = "www.imdb.com" + self.inp["url"], self.inp["imdb_id"]
        id = self.inp["id"]
        dom = lxml.html.fromstring(download(url))
        infobar = lxml.html.tostring(dom.xpath("//div[@class='infobar'][0]")[0])
        metadata = dict(map(
            lambda h4: (
                h4.text.split(":")[0], 
                map(lambda a: lxml.html.tostring(a), h4.xpath("self/following-sibling::a"))
            ),
            dom.xpath("//h4[@class='inline']")   
        ))
        print metadata
                

class NowPlayingScrapeTask(Task):
    def run(self):
        url = self.inp
        dom = lxml.html.fromstring(download(url))
        image_urls = dom.xpath("//img[@class='poster']/attribute::src")
        names = dom.xpath("//a[@class='title']/text()")
        urls = dom.xpath("//a[@class='title']/attribute::href")
        plots = dom.xpath("//span[text()='The Plot:']/following::node()[1]")
        cursor = db.cursor()

        for name, url, image_url, plot in zip(names, urls, image_urls, plots):
            imdb_id = url.split("/")[-1]
            cursor.execute("INSERT IGNORE INTO movies (imdb_id, name, image_url,  plot, created_time)"
                           "VALUES (%s, %s, %s, %s, %d)"\
                           % (MySQLdb.escape_string(imdb_id),\
                              MySQLdb.escape_string(name),\
                              MySQLdb.escape_string(image_url),\
                              MySQLdb.escape_string(plot),\
                              time.time()))
                              
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
