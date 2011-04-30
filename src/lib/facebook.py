from urllib2 import urlopen
from urllib import quote
import demjson

class Facebook:

    @classmethod
    def init(cls, config):
        cls.config = config
    
    @classmethod
    def search(cls, query, limit=10, since=0, lang="en"):
        """search tweets
        
        """
        return demjson.decode(
            urlopen(cls.config["search_url"] % {
                "q"         : quote(query), 
                "type"      : "post",
                "lmit"      : limit, 
                "since"         : since_id,
            }).read(),
            encoding="utf-8"
        )["results"]
