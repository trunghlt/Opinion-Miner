""" Thread Distributor

Ver     : 0.1
Author  : Trung Huynh

"""
from Queue import Queue
from threading import Thread, Lock


class Worker(Thread):
    
    def __init__(self, distributor, name=None):
        Thread.__init__(self)
        self.queue = Queue()
        self.distributor = distributor
        if name is not None: self.name = name
        
    def run(self):
        for task in iter(self.distributor.inp_queue.get, "STOP"):
            task.worker = self
            
            self.distributor.lock.acquire()
            self.distributor.working += 1
            self.distributor.lock.release()
            
            for result in task.run():
                if result is not None:
                    self.distributor.out_queue.put(result)
                    
            self.distributor.lock.acquire()
            self.distributor.working -= 1
            self.distributor.lock.release()
            
            # Stop if no worker is working and queue is empty. It is 
            # reasonable because no new task can be generated at this point.
            if (self.distributor.working == 0) \
            and (self.distributor.inp_queue.empty()):
                self.distributor.stop()
            
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


    class StopTask(Task):
        
        def run(self):
            self.distributor.out_queue.put("STOP")
            yield None


    def __init__(self, n_workers=0):
        self.inp_queue = Queue()
        self.out_queue = Queue()
        self.name_id_map = {}
        self.n_workers = n_workers
        self.workers = []
        self.working = 0
        self.lock = Lock()
        for i in xrange(n_workers):
            self.add_worker()
        
    def send(self, msg, to):
        if type(to) is int:
            self.workers[to].queue.put(msg)
        elif type(to) is str:
            self.workers[self.name_id_map[to]].queue.put(msg)
        
    def add_worker(self, name=None):
        if name is not None: self.name_id_map[name] = self.n_workers
        self.workers.append(Worker(self, name))
        self.n_workers += 1
        
    def run(self):
        for t in self.workers: t.start()
        for t in self.workers: t.join()
        
    def add_task(self, task_class, data=None):
        task = task_class()
        task.distributor = self
        task.inp = data
        self.inp_queue.put(task)
        
    def stop(self):
        self.add_task(ThreadDistributor.StopTask)
        for i in xrange(self.n_workers):
            self.inp_queue.put("STOP")
            
    def results(self):
        for item in iter(self.out_queue.get, "STOP"):
            yield item
        
    
class ComputationTask(Task):
    
    def run(self):
        yield self.inp**2;

    
class InitializeTask(Task):
    
    def run(self):
        for i in xrange(1000):     
            self.distributor.add_task(ComputationTask, i)
            
        yield None

        
if __name__ == "__main__":
    #Test dead lock
    for i in xrange(1000): 
        print i
        distributor = ThreadDistributor(20)
        distributor.add_task(InitializeTask)
        distributor.run()
