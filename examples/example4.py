from threadpool import ThreadPool, ClockThread
import time
import random
import pprint
from threading import Lock

g_print_lock = Lock()


def worker_func(num1, num2):
    time.sleep(random.random() * 2)
    stuff = num1 * num2
    g_print_lock.acquire()
    print("\n", stuff)
    g_print_lock.release()
    return stuff


def some_new_thread(*args):
    print(args)


num_seq1 = list(range(10))
num_seq2 = list(range(10, 20))

# use a dict with the parameter's name and value to pass in more than 1 parameter
work_to_be_done = [{"num1": num_seq1[i], "num2": num_seq2[i]} for i in range(len(num_seq1))]

tp = ThreadPool(work_to_be_done, num_threads=2, verbose=True, cache_return_val=True)
tp.set_default_worker(worker_func)

# we manually add a new thread here
some_new_args = [1, 2, 3]
tp.add_thread(some_new_thread, some_new_args)

tp.start()
tp.sync()
