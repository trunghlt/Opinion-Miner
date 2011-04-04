import re
import os.path
import tornado.ioloop
import tornado.web
import tornado.httpserver
from twitter import Twitter
import config
import credential
import demjson
import memcache
from servers.client import Client, Confidence
from tornado.options import define, options

SAClient = Client(config=config.SENTIMENT["config"], enable_timer=False)
Mem = memcache.Client([config.MEMCAHCE["address"]], debug=0)

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default=credential.DB["host"], help="database host")
define("mysql_database", default=credential.DB["name"], help="database name")
define("mysql_user", default=credential.DB["user"], help="database user")
define("mysql_password", default=credential.DB["passwd"], help="database password")

def retrieve_items(q, rpp=5, since_id=0):
    items = Twitter.search(q, rpp, since_id)
    if len(items) > 0: Mem.set("last_tweet_id", items[0]["id"])

    filtered_items = []
    for item in items: 
        score = SAClient.score(
            item["text"].encode("utf-8"), 
#            return_confidence=True,
#            confidence_type=Confidence.NNP,
        )
        if score:
            item["sentiment"] = score["score"]
            filtered_items.append(item)

    return filtered_items


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/update/([^/]+)", UpdateHandler),
            (r"/([^/]+)", HomeHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        
        Twitter.init(config.TWITTER)
        
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db        


class HomeHandler(BaseHandler):
    def get(self, q):
        self.title = "Next movies to watch"
        items = retrieve_items(q)
        self.render("index.html", title=self.title, items=items, q=q)


class UpdateHandler(BaseHandler):
    def get(self, q):
        items = retrieve_items(q, since_id=Mem.get("last_tweet_id"))
        self.render("update.html", items=items)
        
        
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(7000)
    tornado.ioloop.IOLoop.instance().start()        
