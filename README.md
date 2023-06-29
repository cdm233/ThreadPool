# ThreadPool
A simple thread pool library for me, maybe you'd find it helpful too. Use this if you don't want to write the same 10-20 lines every single time. Or if you wish to keep a reminder of how a thread pool works on your side. 
Note: Still in the planning phase.

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
Return value:
{'thread 0': [{'iteration': 0, 'param': 0, 'return value': 0},
              {'iteration': 1, 'param': 16, 'return value': 320}],
 'thread 1': [{'iteration': 0, 'param': 1, 'return value': 20},
              {'iteration': 1, 'param': 17, 'return value': 340}],
 'thread 10': [{'iteration': 0, 'param': 10, 'return value': 200}],
 'thread 11': [{'iteration': 0, 'param': 11, 'return value': 220}],
 'thread 12': [{'iteration': 0, 'param': 12, 'return value': 240}],
 'thread 13': [{'iteration': 0, 'param': 13, 'return value': 260}],
 'thread 14': [{'iteration': 0, 'param': 14, 'return value': 280}],
 'thread 15': [{'iteration': 0, 'param': 15, 'return value': 300}],
 'thread 2': [{'iteration': 0, 'param': 2, 'return value': 40},
              {'iteration': 1, 'param': 18, 'return value': 360}],
 'thread 3': [{'iteration': 0, 'param': 3, 'return value': 60},
              {'iteration': 1, 'param': 19, 'return value': 380}],
 'thread 4': [{'iteration': 0, 'param': 4, 'return value': 80}],
 'thread 5': [{'iteration': 0, 'param': 5, 'return value': 100}],
 'thread 6': [{'iteration': 0, 'param': 6, 'return value': 120}],
 'thread 7': [{'iteration': 0, 'param': 7, 'return value': 140}],
 'thread 8': [{'iteration': 0, 'param': 8, 'return value': 160}],
 'thread 9': [{'iteration': 0, 'param': 9, 'return value': 180}]}


Process finished with exit code 0
```

## Quick Example 2
If your worker function takes in more than 1 parameter.
```python
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

# let's use 5 threads
tp = ThreadPool(work_to_be_done, num_threads=5, verbose=True, cache_return_val=True)

# the library automatically create a wrapper for you worker, note that the worker must be working on a single item from "work"
tp.set_worker(worker_func)

tp.start()
tp.sync()

print("Return value:")
pprint.pprint(tp.get_ret_val())
```
output:

```
Work distributed.
ThreadPool initialized.
  ThreadPool Progress Tracker: 10/10, est: 0.00s.
All threads synchronized.
Return value:
{'thread 0': [{'iteration': 0,
               'param': {'num1': 0, 'num2': 10},
               'return value': 0},
              {'iteration': 1,
               'param': {'num1': 5, 'num2': 15},
               'return value': 75}],
 'thread 1': [{'iteration': 0,
               'param': {'num1': 1, 'num2': 11},
               'return value': 11},
              {'iteration': 1,
               'param': {'num1': 6, 'num2': 16},
               'return value': 96}],
 'thread 2': [{'iteration': 0,
               'param': {'num1': 2, 'num2': 12},
               'return value': 24},
              {'iteration': 1,
               'param': {'num1': 7, 'num2': 17},
               'return value': 119}],
 'thread 3': [{'iteration': 0,
               'param': {'num1': 3, 'num2': 13},
               'return value': 39},
              {'iteration': 1,
               'param': {'num1': 8, 'num2': 18},
               'return value': 144}],
 'thread 4': [{'iteration': 0,
               'param': {'num1': 4, 'num2': 14},
               'return value': 56},
              {'iteration': 1,
               'param': {'num1': 9, 'num2': 19},
               'return value': 171}]}

Process finished with exit code 0
```
