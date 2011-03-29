import os.path
import tornado.ioloop
import tornado.web
import tornado.httpserver


class Application(tornado.web.Application):
    def __int__(self):
        handlers = [
            (r"/", HomeHandler)
        ]
        settings = dict(
            template_path=os.path.joins(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static")
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        items = ["Movie 1", "Movie 2", "Movie 3"]
        self.render("index.html", title="What should you watch next?", items=items)

        
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()        
