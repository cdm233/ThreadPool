from threadpool import ThreadPool
import time
import pprint


def worker_func(num1, num2):
    time.sleep(1)
    stuff = num1 * num2
    return stuff


num_seq1 = list(range(10))
num_seq2 = list(range(10, 20))

# use a dict with the parameter's name and value to pass in more than 1 parameter
work_to_be_done = [{"num1": num_seq1[i], "num2": num_seq2[i]} for i in range(len(num_seq1))]

# let's use 4 threads
tp = ThreadPool(work_to_be_done, num_threads=5, verbose=True, cache_return_val=True)

# the library automatically create a wrapper for you worker, note that the worker must be working on a single item from "work"
tp.set_default_worker(worker_func)

tp.start()
tp.sync()

print("Return value:")
pprint.pprint(tp.get_ret_val())
