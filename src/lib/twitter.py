from urllib2 import urlopen
from urllib import quote
import demjson
import re

class Twitter:
    url_regex = re.compile(r"\b(((https?|ftp|file)?://)|(www\.))[-A-Z0-9+&@#/%?=~_|!:,.;]*[-A-Z0-9+&@#/%=~_|]", re.I)
    mention_regex = re.compile(r"((@|#)\S+)", re.I)

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
    
    @staticmethod
    def underscorize(matchobj):
        return "_" * len(matchobj.group(0))
        
    @staticmethod
    def clean(text, *names):
        s = re.sub(Twitter.mention_regex, Twitter.underscorize, text)
        s = re.sub(Twitter.url_regex, Twitter.underscorize, s)
        for name in names:
            regex = re.compile(name, re.I)
            s = re.sub(regex, Twitter.underscorize, s)
            
        return s
        
        
if __name__ == "__main__":
    print Twitter.clean("@basodi #keyword http://lfgjkfdjg.com www.google.com sdjfhdskfh") 
    print Twitter.clean("I am watching Scream 4 (w/447 others) http://bit.ly/agu3HC @GetGlue #Scream4", "Scream 4")
    print Twitter.clean("Rock in Rio for me. =(: http://t.co/dm6hH8z", "Rio")
    print Twitter.clean("Vaaaai no Rock in Rio?? (@matheusherriez live on http://twitcam.com/4k90w)", "Rio")
