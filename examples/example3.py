from threadpool import ThreadPool
import time
import pprint

import threading

print_lock = threading.Lock()


def worker_func(num1, num2):
    time.sleep(1)
    stuff = num1 * num2
    return stuff


def worker_wrapper(work):
    for w in work:
        print_lock.acquire()
        print(worker_func(**w))
        print_lock.release()


num_seq1 = list(range(5))
num_seq2 = list(range(5))

# use a dict with the parameter's name and value to pass in more than 1 parameter
work_to_be_done = [{"num1": num_seq1[i], "num2": num_seq2[i]} for i in range(len(num_seq1))]

# let's use 4 threads
tp = ThreadPool(work_to_be_done, num_threads=4, verbose=True, cache_return_val=True)

# if you want to use your own worker wrapper and manage the thread pool yourself
dw = tp.get_distributed_work()
etp = tp.create_thread_pool(worker_wrapper, dw)

# these functions still work, just pass in the external threadpool
tp.start(etp)
tp.sync(etp)
