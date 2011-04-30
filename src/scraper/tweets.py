import logging
import MySQLdb
from lib import twitter
from thread_distributor import ThreadDistributor, Task
from www.credential import DB

N_THREADS = 20
# search for only movies created in db no older than TIME_TH days
TIME_TH = 2*30
db_connect = MySQLdb.connect(DB["host"], DB["user"], DB["passwd"], DB["name"])
cursor = db_connect.cursor()


class InitializeTask(Task):
    """ Read tweet from database for recent movie
    
    """
    
    def run(self):
        cursor.execute("""SELECT `id`, `name` FROM movies
                       WHERE DATEDIFF(NOW(), created_time) <= %s""", 
                       TIME_TH)
        movies = cursor.fetchall()
        print movies
        
        yield None


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        filename = "logs/tweets_error.log",
        filemod = "w",
        format="%(asctime)s\t%(levelname)s\t(%(threadName)-10s)\t%(message)s"
    )
    distributor = ThreadDistributor(N_THREADS)
    distributor.add_task(InitializeTask)
    distributor.run()
    cursor.close()
