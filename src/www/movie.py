import re
import os.path
import tornado.ioloop
import tornado.web
import tornado.httpserver
from twitter import Twitter
import config

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        
        # init twitter api
        Twitter.init(config.TWITTER)
        
        tornado.web.Application.__init__(self, handlers, **settings)


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        items = map(lambda re: re["text"], Twitter.search("movie", rpp=20))
        self.render("index.html", title="What should you watch next?", items=items)

        
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()        
