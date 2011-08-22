import confidential
import tornado.database
from tornado.options import define, options

TWITTER = {
    "api_key"           : "NJttATizykZ2uyRR9OSnQ",
    "consumer_key"      : "NJttATizykZ2uyRR9OSnQ",
    "consumer_secret"   : "dc4zCuMSfzlZwG1B0z1tViNV07piolgGaFOOvkxpKQ",
    "request_token_url" : "https://api.twitter.com/oauth/request_token",
    "access_token_url"  : "https://api.twitter.com/oauth/access_token",
    "authorize_url"     : "https://api.twitter.com/oauth/authorize",
    "search_url"        : "http://search.twitter.com/search.json?"
                          "q=%(q)s&rpp=%(rpp)d&since_id=%(since_id)d&lang=%(lang)s",
}

SENTIMENT = dict (
    config	= "../servers/server.cfg"
)

MEMCACHE = dict(
    address = "127.0.0.1:11211",
)

NNP_CFD_THRESHOLD = 0.02

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default=confidential.DB["host"], help="database host")
define("mysql_database", default=confidential.DB["name"], help="database name")
define("mysql_user", default=confidential.DB["user"], help="database user")
define("mysql_password", default=confidential.DB["passwd"], help="database password")

db = tornado.database.Connection(
    host=options.mysql_host, database=options.mysql_database,
    user=options.mysql_user, password=options.mysql_password
)
