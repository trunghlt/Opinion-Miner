import urllib2

def download(url, max_retries=5, verbose=True):    
    """Content downloaded from ``url``, maximum retry number is set by 
    ``max_retries``.
        
    """
    for i in xrange(max_retries):
        try:
            return urllib2.urlopen(url).read()
        except Exception, e:
            if verbose: print "Retries: %d, url: %s" % (i + 1, url)
    
    return None
    
