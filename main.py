import multiprocessing
from multiprocessing import Queue
from worker import worker
from server import run

if __name__ == '__main__':
    job_queue_1 = Queue()
    job_queue_2 = Queue()
    proc0 = multiprocessing.Process(target=run)
    proc1 = multiprocessing.Process(target=worker, args=(1, job_queue_1))
    proc2 = multiprocessing.Process(target=worker, args=(2, job_queue_2))
    proc0.start()
    proc1.start()
    proc2.start()