import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        items = ["Movie 1", "Movie 2", "Movie 3"]
        self.render("index.html", title="What should you watch next?", items=items)
        
application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()        
