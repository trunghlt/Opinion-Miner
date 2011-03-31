from urllib2 import urlopen
from urllib import quote
import demjson

class Twitter:

    @classmethod
    def init(cls, config):
        cls.config = config
    
    @classmethod
    def search(cls, query, rpp=10, since_id=0, lang="en"):
        """search tweets
        
        """
        return demjson.decode(
            urlopen(cls.config["search_url"] % {
                "q"         : quote(query), 
                "rpp"       : rpp, 
                "since_id"  : since_id,
                "lang"      : lang
            }).read(),
            encoding="utf-8"
        )["results"]
