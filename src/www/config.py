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
    address = "127.0.0.1:11212",
)

NNP_CFD_THRESHOLD = 0.02
