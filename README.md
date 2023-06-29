# ThreadPool
A simple thread pool library for python. Use this if you don't want to write the same 10-20 lines every single time. Or if you wish to keep a reminder of how a thread pool works on your side. 

## Quick Example1
The standard way of using it.
```python
from threadpool import ThreadPool
import time


def worker_func(num):
    time.sleep(1)
    stuff = num * 10
    stuff *= 2
    return stuff


work_to_be_done = range(20)

# let the library decide for you how many threads to use, or you can just pass in an integer, e.g. 12
tp = ThreadPool(work_to_be_done, num_threads=-1, verbose=True)

# the library automatically create a wrapper for you worker, note that the worker must be working on a single item from "work"
tp.set_worker(worker_func)

tp.start()
tp.sync()
print(f"Return values are: {tp.get_ret_val()}")
```

Output:
```
Using 16 threads.
Work distributed.
ThreadPool initialized.
  ThreadPool Progress Tracker: 20/20, est: 0.00s.
All threads synchronized.
Return values are: [[0, 320], [20, 340], [40, 360], [60, 380], [80], [100], [120], [140], [160], [180], [200], [220], [240], [260], [280], [300]]

Process finished with exit code 0
```

## Quick Example 2
If your worker function takes in more than 1 parameter.
```python
from threadpool import ThreadPool
import time


def worker_func(num1, num2):
    time.sleep(1)
    stuff = num1 * num2
    return stuff


num_seq1 = list(range(20))
num_seq2 = list(range(10, 30))

# use a dict with the parameter's name and value to pass in more than 1 parameter
work_to_be_done = [{"num1": num_seq1[i], "num2": num_seq2[i]} for i in range(len(num_seq1))]

# let's use 4 threads, note: if cache_return_val is not set, get_ret_val will fail
tp = ThreadPool(work_to_be_done, num_threads=4, verbose=True, cache_return_val=True)

# the library automatically create a wrapper for you worker, note that the worker must be working on a single item from "work"
tp.set_worker(worker_func)

tp.start()
tp.sync()

print(f"Return values are: {tp.get_ret_val()}")
```
output:

```
Work distributed.
ThreadPool initialized.
  ThreadPool Progress Tracker: 20/20, est: 0.00s.
All threads synchronized.
Return values are: [[0, 56, 144, 264, 416], [11, 75, 171, 299, 459], [24, 96, 200, 336, 504], [39, 119, 231, 375, 551]]

Process finished with exit code 0
```
