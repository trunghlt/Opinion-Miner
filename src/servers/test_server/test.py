import csv
import sys
from threading import Thread, Lock
from Queue import Queue 
from servers.client import Client, Confidence

N_THREADS = 10
SAMPLES = 10000
CONFIDENCE_THRESHOLD = 0.02


TEST = {
    "default":  "short.txt",
    "short":    "short.txt",
}

test_file = TEST["short"]        
if len(sys.argv) > 1:    
    test_key = sys.argv[1].lower()
    test_file = TEST.get(test_key, "default")

lock = Lock()


def nnp_class(c):
    """convert class number from 1-5 scale to negative-neutral-positive
    
    The function returns negative, neutral or positive respectively.
    
    ``c``: class number in 1-5 scale.
    
    """
    if c in set([1,2]): return "negative"
    elif c in set ([4,5]): return "positive"
    else: return "neutral"

                    
class MyThread(Thread):

    def __init__(self, id, workQueue, total, cm):
        self.id = id        
        self.workQueue = workQueue
        self.total = total
        self.cm = cm
        self.client = Client(config="../server.cfg", enable_timer=True)
        Thread.__init__(self)
        

    def test_sent(self, return_confidence=True,
                        confidence_type = Confidence.LOCAL,
                        confidence_threshold=CONFIDENCE_THRESHOLD):
        """ Test sentiment scoring
        
        ``return_confidence``: whether or not the sentiment client computes
        confidence score for each prediction.
        
        ``confidence_threshold``: confidence threshold for building 
        confusion matrix. Default value is %f.
        
        """  % (CONFIDENCE_THRESHOLD)
        for work in iter(self.workQueue.get, "STOP"):
            data = work["data"]
            id = work["id"]
            real_sent, review = int(data[0]), data[1]           
            svm = self.client.score(review, return_confidence, confidence_type)
            
            if not return_confidence or svm["confidence"] > confidence_threshold:
                self.total[real_sent] += 1
                self.cm[real_sent][int(svm["score"])] += 1
            
            if id % 1000 == 0: print id
            
            
    def test_probs(self):
        for work in iter(self.workQueue.get, "STOP"):
            data = work["data"]
            id = work["id"]
            real_sent, review = data[0], data[1]
            svm = self.client.score(review)
            predicted_sent = svm["score"]

            max_prob_sent = max(zip(svm["probs"].keys(), svm["probs"].values()),
                                key = lambda x: x[1])

            raise Exception("Predicted score is different from the score with "
                             "maximum probability: (%d, %d)"\
                             % (predicted_sent, max_prob_sent))
     
                
    def run(self):
        self.test_sent(return_confidence=False,
                       confidence_type=Confidence.LOCAL)

        
if __name__ == "__main__":
    fi = csv.reader(open(test_file), delimiter="\t", quotechar="\"")

    total = [0 for i in xrange(6)]
    cm = [[0 for i in xrange(6)] for j in xrange(6)]
    i = 0 
    workQueue = Queue()
    for row in fi:
        workQueue.put({"id": i, "data": row})
        i += 1
        if i >= SAMPLES: break

    for i in xrange(N_THREADS): workQueue.put("STOP")

    threads = [MyThread(i, workQueue, total, cm) for i in xrange(N_THREADS)]

    for t in threads: t.start()
    for t in threads: t.join()

    print total
    for i in xrange(1, 6):	
	    for j in xrange(1, 6):
		    print int(float(cm[i][j]) / total[i] * 100), "\t",
	    print
	    
