import os
import time
import socket
import demjson
from ConfigParser import ConfigParser

EPS = 0.001
SCALE = 10


def recvall(socket):
    data = ""
    while True:
        chunk = socket.recv(1024)
        if not chunk: break
        data = data + chunk
    return data
    
    
def decimal2float_dict(dec_dict):
    return dict(map(lambda x: (x[0], float(x[1])), dec_dict.items()))
    

class Confidence:

    LOCAL, NNP = range(2)    

    def __init__(self, score_map, eps=EPS, scale=SCALE):
        """create a confidence object
        
        ``score_map``: a dictionary of Condition Probability in each class. Its
        for mat is {1: score, 2: score, 3: score, 4: score, 5: score}. This
        is normally the result["probs"] returned from the sentiment server.            
        
        ``eps``: the minimum estimated Conditional Probability.
        
        ``scale``: the scale of confidence score for normalisation.       
         
        """
        self.score_map = score_map
        
        self.sorted_scores = sorted( \
            score_map.items(), \
            key     = lambda x: x[1], \
            reverse = True \
        )
        
        self.eps = eps
        self.scale = scale


    #rescaled confidence score
    def norm(self, cfd): return cfd * self.eps * self.scale
    
    
    #local confidence score of predicted class
    def local(self): 
        return self.norm(self.sorted_scores[0][1] / self.second_norm(self.sorted_scores[1][1]))


    # normalize second largest score, =1 if negative
    @classmethod
    def second_norm(cls, score):
        n = score if score > 0 else EPS
        return n 
    
    # NNP confidence score in the 3 class space - negative, neutral, possitive
    def nnp(self):
        class_max, score_max = self.sorted_scores[0]
        if (class_max in set(["4","5"])):
            return self.norm(
                score_max / self.second_norm(max(map(lambda i: self.score_map[i], ["1", "2", "3"]))) 
            )
        elif (class_max in set(["1","2"])):
            return self.norm(
                score_max / self.second_norm(max(map(lambda i: self.score_map[i], ["3", "4", "5"])))
            )
        else:
            return self.norm(
                score_max / self.second_norm(max(map(lambda i: self.score_map[i], ["1", "2", "4", "5"])))
            )    
            
            
    def val(self, confidence_type=LOCAL):
        """ confidence score
        
        ``confidence_type``: Confidence.LOCAL => return self.local(), 
        Confidence.NNP => return self.NNP().
        """
    
        if confidence_type == Confidence.LOCAL:
            return self.local()
        elif confidence_type == Confidence.NNP:
            return self.nnp()
        else:
            return None
            
class Client(object):

    HOST = "127.0.0.1"
    PORT = 9990
    TIMEOUT = 30
    TRIES = 10

    def __init__(self, host=None, port=None, timeout=None, tries=None, enable_timer=False, config=None):

        self.host = Client.HOST
        self.port = Client.PORT
        self.timeout = Client.TIMEOUT
        self.tries = Client.TRIES
    
        if config:
            cfg = ConfigParser()
            cfg.readfp(open(config))
            self.host = cfg.get("socket", "host")
            self.port = int(cfg.get("socket", "port"))
            self.timeout = int(cfg.get("socket", "timeout"))
            self.tries = int(cfg.get("socket", "max_tries"))
            self.feature_weights = int(cfg.get("output", "feature_weights"))
            self.class_weights = int(cfg.get("output", "class_weights"))
    
        if host: self.host = host
        if port: self.port = port
        if timeout: self.timeout = timeout
        if tries: self.tries = tries
                
    def score(self, review, 
                    return_confidence=False, 
                    confidence_type=Confidence.LOCAL):
        """Return sentiment information of review
        
        ``review``: input text content 
        
        ``return_confidence = True`` then the function returns confidence 
        of scoring 
        
        ``confidence_type``: local (Confidence.LOCAL) or NNP (Confidence.NNP) 
        (negative/neutral/positive). 
        
        """
    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        
        tries = 0        
        while True:
            try:
                self.sock.connect((self.host, self.port))
                break
            except Exception, e:                
                tries += 1
                if tries >= self.tries:
                    return False
                
        tries = 0
        while True:
            try:
                self.sock.send(review)
                break
            except Exception, e:
                print e
                tries += 1
                if tries >= self.tries:
                    self.sock.close()
                    return False
        
        tries = 0     
        while True:
            try:
                data_str = recvall(self.sock)
                break
            except Exception, e:
                tries += 1
                if tries >= self.tries:
                    self.sock.close()
                    return False
            
        self.sock.close()
        
        data = demjson.decode(data_str)
        
        # convert class weights from decimal to float if available
        if data.has_key("weights"):
            data["weights"] = decimal2float_dict(data["weights"])
            
        # convert feature weights from decial to float if available
        if data.has_key("features"):
            for f in data["features"]: 
                f["weights"] = decimal2float_dict(f["weights"])
                
        # return confidence score if required
        if return_confidence:
            if not data.has_key("weights"):
                raise Exception("The sentiment server does not return class "
                                "weights for confidence scoring")
            cfd = Confidence(data["weights"])
            data["confidence"] = cfd.val(confidence_type)
            
        return data

if __name__ == "__main__":
    client = Client(config="server.cfg", enable_timer=True)   
    print client.score("If you can imagine a soothing blend of jojoba oils, \
vanilla, and WD40 being poured into both ear holes simultaneously, then you \
will have only been able to scratch the surface of the feast of pleasure that \
is Katie And Pete's A Whole New World Album. Similar in it's ambition to \
Wagner's ring cycle but less German, A Whole New World is one of the best \
sound combinations that has ever been recorded. I also found the case very \
useful for replacing a tile that had been missing in my bathroom for the past \
two and a half years. A TRIUMPH! ESPECIALLY SUITABLE FOR THOSE WITH TILED \
BATHROOMS")
