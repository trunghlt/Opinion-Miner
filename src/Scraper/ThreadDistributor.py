from Queue import Queue
from threading import Thread

class Worker(Thread):
    
    def __init__(self, distributor, name=None):
        self.name = name
        self.queue = Queue()
        self.distributor = distributor
        Thread.__init__(self)
        
    def run(self):
        for task in iter(self.distributor.inp_queue.get, "STOP"):
            task.worker = self
            for result in task.run():
                self.distributor.out_queue.put(result)
                
    def send(self, msg, to):
       self.distributor.send(msg, to) 
    
    
class Task:

    def __init__(self):
        self.distributor = None
        self.worker = None
        self.inp = None
        
    def run(self):
        raise NotImplementedError    
    

class ThreadDistributor:

    def __init__(self):
        self.inp_queue = Queue()
        self.out_queue = Queue()
        self.workers = []
        self.name_id_map = {}
        self.n_workers = 0
        
    def send(self, msg, to):
        if type(to) is int:
            self.workers[to].queue.put(msg)
        elif type(to) is str:
            self.workers[self.name_id_map[to]].queue.put(msg)
        
    def add_worker(self, name=None):
        if name is not None: self.name_id_map[name] = self.n_workers
        self.workers.append(Worker(self, name))
        
    def run(self):
        for t in self.workers: t.start()
        for t in self.workers: t.join()
        
    def add_task(self, data, task):
        task.distributor = self
        task.inp = data
        self.inp_queue.put(task)
        
    def stop(self):
        for i in xrange(self.n_workers):
            self.inp_queue.put("STOP")
        
    
class SquareTask(Task):
    
    def run(self):
        yield self.inp**2;

    
class InitializeTask(Task):
    
    def run(self):
        for i in xrange(5):     
            self.distributor.add_task(i, SquareTask())
        self.distributor.stop()
        
if __name__ == "__main__":
    distributor = ThreadDistributor()
    for i in xrange(10): distributor.add_worker()
    distributor.add_task(None, InitializeTask())
    distributor.run()
    for v in distributor.out_queue.get():
        print v
