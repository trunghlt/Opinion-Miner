import re
import os.path
import tornado.ioloop
import tornado.web
import tornado.httpserver
from twitter import Twitter
from data_processing import utils
import config
import credential
import demjson
import memcache
import lxml.html
from servers.client import Client, Confidence
from tornado.options import define, options
import tornado.database

SAClient = Client(config=config.SENTIMENT["config"], enable_timer=False)
Mem = memcache.Client([config.MEMCACHE["address"]], debug=0)


def retrieve_items(q, rpp=5, since_id=0):
    items = Twitter.search(q, rpp, since_id)
    if len(items) > 0: Mem.set("last_tweet_id", items[0]["id"])

    filtered_items = []
    for item in items: 
        filtered_text = Twitter.clean(item["text"], q)
        score = SAClient.score(
            filtered_text.encode("utf-8"), 
            return_confidence=True,
            confidence_type=Confidence.NNP,
        )

        if score and score["confidence"] > config.NNP_CFD_THRESHOLD:
            item["sentiment"] = score["score"]
            print filtered_text, score["weights"]
        else:
            item["sentiment"] = "-"
            
        if item["sentiment"] in set(["-", "3"]): 
            item["nnp"] = "neutral"
        elif item["sentiment"] in set(["1", "2"]):
            item["nnp"] = "negative"
        elif item["sentiment"] in set(["4", "5"]):
            item["nnp"] = "positive"

    return items
    
    
def parse_settings(db):
    key_value_pairs = db.query("SELECT * FROM settings");
    settings = {}
    for p in key_value_pairs:
        settings[p.key] = p.value
        
    return settings


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/update/([^/]+)", UpdateHandler),
            (r"/([^/]+)", SearchHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        
        Twitter.init(config.TWITTER)
        
        tornado.web.Application.__init__(self, handlers, **settings)
        
        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)       
            
        self.settings.update(parse_settings(self.db)) 


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db        


class IndexHandler(BaseHandler):
    
    def get(self):
        self.title = "Top hot movies"
        self.render(
            "index.html", 
            title=self.title, 
            movies=self.get_movies(), 
            settings=self.application.settings,
        )
        
    def get_movies(self):
        movies = self.db.query("SELECT * FROM movies ORDER BY created_time DESC")
        for movie in movies:
            for key in ["infobar", "Writers", "Directors", "Stars"]:
                o = self.db.get("SELECT value FROM metadata "
                                "WHERE (movie_id=%s AND `key`=%s)",
                                 movie.id, key)
                if o is None: setattr(movie, key, None)
                else:
                    setattr(movie, key,
                            lxml.html.fromstring(o.value).text_content().strip())                                                     
                    
        return movies


class SearchHandler(BaseHandler):
    def get(self, q):
        self.title = "Next movies to watch"
        items = retrieve_items(q)
        self.render("search.html", title=self.title, items=items, q=q)


class UpdateHandler(BaseHandler):
    def get(self, q):
        items = retrieve_items(q, since_id=Mem.get("last_tweet_id"))
        self.render("update.html", items=items)
        
    
def run():    
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(7000)
    tornado.ioloop.IOLoop.instance().start()        

if __name__ == "__main__":
    run()

