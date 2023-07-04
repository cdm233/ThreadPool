from threadpool import ThreadPool
import time
import pprint


def worker_func(num):
    time.sleep(1)
    stuff = num * 10
    stuff *= 2
    return stuff


work_to_be_done = range(20)

# let the library decide for you how many threads to use, or you can just pass in an integer, e.g. 12
tp = ThreadPool(work_to_be_done, num_threads=-1, verbose=True)

# the library automatically create a wrapper for you worker, note that the worker must be working on a single item from "work"
tp.set_default_worker(worker_func)

tp.start()
tp.sync()

print("Return value:")
pprint.pprint(tp.get_ret_val())
