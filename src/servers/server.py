import threading
import socket
import SocketServer
import logging
import logging.handlers
import demjson
from linear_svm import LinearSVM
from argparse import ArgumentParser
from ConfigParser import ConfigParser

LEVELS = {'debug': logging.DEBUG,\
          'info': logging.INFO,\
          'warning': logging.WARNING,\
          'error': logging.ERROR,\
          'critical': logging.CRITICAL,\
          'quiet': logging.NOTSET}

if __name__ == "__main__":
    parser = ArgumentParser(description="Musicmetric Sentiment Analysis Server")
    parser.add_argument("--config", dest="config", default="server.cfg")
    parser.add_argument("--stop", dest="stop", default=False, const=True, nargs="?")
    parser.add_argument("--host", dest="host", default=None)
    parser.add_argument("--user", dest="user", default=None)
    parser.add_argument("--passwd", dest="passwd", default=None)
    parser.add_argument("--db", dest="db", default=None)                        
    args = parser.parse_args()
    
    config = ConfigParser()
    try:
        config.readfp(open(args.config))
    except Exception, e:
        raise Exception("Can't parse config file %s:: %s" % (args.config, e))
        
    try:
        DIR = config.get("database", "path")
        MODEL_FILENAME = DIR + "/" + config.get("database", "model")
        WORD_ORDER_FILENAME = DIR + "/" + config.get("database", "index")
        HOST = config.get("socket", "host")
        PORT = int(config.get("socket", "port"))
        MAX_REVIEW_SIZE = int(config.get("data", "maxsize"))
        LOG = config.get("runtime", "log")
        LOG_SIZE = config.get("runtime", "log_size")
        MODE = LEVELS.get(config.get("runtime", "mode"), logging.NOTSET)
    except Exception, e:
        raise Exception("Invalid config file:: %s" % e)

    wordOrder = {}
    outRows = []
    count = 0
    musicEntityNames = {}

    logger = logging.getLogger("SAServer")
    logger.setLevel(MODE)
    loggingHandler = logging.handlers.RotatingFileHandler(LOG, maxBytes=int(LOG_SIZE), backupCount=5)
    loggingHandler.setFormatter(logging.Formatter("%(asctime)s - (%(threadName)-10s) - %(levelname)s - %(message)s"))
    logger.addHandler(loggingHandler)

#---------------------------------------------------------------------------------
def readWordOrder():
    global wordOrder
    fi = csv.reader(open(WORD_ORDER_FILENAME), delimiter="\t")
    for row in fi:
        try:
            wordOrder[row[0]] = int(row[1])
        except:
            print row

#---------------------------------------------------------------------------------------------------------
def getNormName(s):
    """
    Get normalised string of s. Look at the regexp for normalising rule detail.
    @param s: input string
    @return normalised version
    """
    return " ".join(re.findall(r"(\b[a-z0-9]+\b)|\(|\)", s.lower()))

#---------------------------------------------------------------------------------
def lookup(s):
    m = hashlib.md5()
    m.update(s)
    return  orderCol[md5Col.index(m.digest())]

#---------------------------------------------------------------------------------
class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(MAX_REVIEW_SIZE)
        
        if self.data.lower() == "[stop]":
            print "Server is terminating... Please wait!"
            logger.debug("Server is terminating...")            
            self.server.terminate()
            self.request.send("0")

        else:            
            predicted_class = LinearSVM.predict(self.data)
            result = {"score": predicted_class}
            self.request.send(demjson.encode(result, encoding="utf-8"))
            logger.debug("%s: %s" % (self.data, predicted_class))
            
#---------------------------------------------------------------------------------
class MyTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, serverAddress, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, serverAddress, RequestHandlerClass)

    def terminate(self):
        self.shutdown()

#---------------------------------------------------------------------------------
def predictor():

    print "Loading svm model..."
    LinearSVM.init(args.config)
    LinearSVM.db_connect(args.host, args.user, args.passwd, args.db)

    server = MyTCPServer((HOST, PORT), MyTCPHandler)
    print "Server started. Listening for reviews..."
    server.serve_forever()

#---------------------------------------------------------------------------------
def stop():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.send("[stop]")
        print "Sent a terminating signal to the server, please wait until it stops!"
        received = sock.recv(1)
        sock.close()
    except:
        print "Error:: Can't connect to the server. Maybe it is not running!"    

#---------------------------------------------------------------------------------
if __name__ == "__main__":
    if args.stop:
        stop()
    else:
        predictor()


