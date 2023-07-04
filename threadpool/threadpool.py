import threading
import time
import multiprocessing as mp
import math
import queue


class ThreadPool:
    def __init__(self, work, num_threads=-1, verbose=False, cache_return_val=True):
        """
        A basic threadpool that does three things: distribute work, start work, sync.
        Make sure the worker is thread-safe, as this is a ThreadPool, not a monitor.
        :param num_threads: Number of threads to use, set to -1 to let the library decide
        :param work: Total work, this should be a list of all work, e.g.: [{}, {}, ...]
        :param verbose: Verbose, whether to print out stuff or not
        :param mode: if num_threads is -1, then this decides how the final number of threads is determined
        """

        # assert checks, order matters
        assert num_threads != 0, "Num_threads must be -1 or a positive integer!"
        assert num_threads >= -1, "Num_threads must be -1 or a positive integer!"
        assert isinstance(num_threads, int), "Num_threads must be -1 or a positive integer!"

        if num_threads == -1:
            max_num_threads = mp.cpu_count()
            proper_num_threads = math.gcd(max_num_threads, len(work))

            # if the gcd is more than 75% of the cpu_count, then use that many threads, otherwise use all
            if proper_num_threads > int(max_num_threads * 0.75):
                self.num_threads = proper_num_threads
            else:
                self.num_threads = max_num_threads

            if verbose:
                print(f"Using {self.num_threads} threads.")

        else:
            self.num_threads = num_threads

        self.total_work = work
        self.__stop_event = threading.Event()

        # printing
        self.verbose = verbose
        self.__progress = 0
        self.__total_time_elapsed = 0
        self.__print_lock = threading.Lock()
        self.__total_progress = len(work)

        self.distributed_work = self.distribute_work(work)
        self.__return_val_cache = {}

        if self.verbose:
            print("Work distributed.")

        # internal threadpool list
        self.__thread_pool = []

        # please don't modify this
        self.__worker_set = False
        self.cache_return_val = cache_return_val

        if self.verbose:
            print("ThreadPool initialized.")

    def distribute_work(self, total_work):
        """
        Distributes the given work among threads evenly.
        It is encouraged that each item within the "total_work" is a dict so the worker can work on multiple parameters.

        :param total_work: List of all work
        :return: A list of lists, where each inner list is work for a single thread
        """
        temp_split = [[] for _ in range(self.num_threads)]
        for idx, work in enumerate(total_work):
            temp_split[idx % self.num_threads].append(work)

        return temp_split

    @staticmethod
    def __worker():
        """
        Placeholder for the worker function that will be set by the user.
        """
        return None

    def __print_progress(self):
        """
        Prints the progress of the thread pool.
        """
        avg_time_per_task = self.__total_time_elapsed / (self.__progress if self.__progress != 0 else 0)
        est_remaining_time = avg_time_per_task * (self.__total_progress - self.__progress) / self.num_threads

        print(f"\r  ThreadPool Progress Tracker: {self.__progress}/{self.__total_progress}, est: {est_remaining_time:.2f}s.", end="")

    def __worker_wrapper(self, thread_id, work):
        """
        Wrapper for the worker function that iterated through the distributed work.
        It also handles error catching and progress tracking.

        :param thread_id: ID of the current thread
        :param work: List of work for the current thread
        :return: True if no errors occurred, False otherwise
        """

        # List to store the return values of each work item processed by this thread
        for idx, w in enumerate(work):
            if self.__stop_event.is_set():
                if self.verbose:
                    print()
                    print(f"\rStop event triggered, stopping thread {thread_id}...")
                return False

            ite_start = time.time()
            try:
                if isinstance(w, dict):
                    # if the arg type is dict, then we unpack the dict so the function sees the parameters as they were
                    cur_ret_val = self.__worker(**w)
                else:
                    # if the arg type is list or anything else, just pass it in
                    cur_ret_val = self.__worker(w)
            except:
                print(f"A fatal error occurred at thread {thread_id}.")
                return False

            ite_end = time.time()

            # create the array if it's the first iteration
            if f"thread {thread_id}" not in self.__return_val_cache:
                self.__return_val_cache[f"thread {thread_id}"] = []

            # Store the return value of the worker function, if it exists
            if (cur_ret_val is not None) and self.cache_return_val:
                self.__return_val_cache[f"thread {thread_id}"].append({
                    "param": w,
                    "iteration": idx,
                    "return value": cur_ret_val
                })

            # Print progress update, if verbose mode is enabled
            if self.verbose:
                # Lock the print statement to prevent other threads from interrupting it
                self.__print_lock.acquire()
                self.__progress += 1
                self.__total_time_elapsed += ite_end - ite_start
                self.__print_progress()
                self.__print_lock.release()

        return True

    def create_thread_pool(self, worker=None, distributed_work=None):
        """
        Creates threadpool. Optionally pass in a callable function here to craete a manually managed threadpool.
        Use this if you don't trust the wrapper created for you and want to manage the working threads yourself.
        Note, if you pass in a function here, then you need to pass this thread_pool to start(thread_pool) and sync(thread_pool).
        :return: thread_pool if worker is set, otherwise none
        """

        if worker is not None:
            assert distributed_work is not None, "External distributed_work is not given!"
            # here we set the worker but don't set the flag, because this threadpool is meant to be external
            temp_thread_pool = []
            for thread_id in range(self.num_threads):
                cur_thread = threading.Thread(
                    target=worker, args=(distributed_work[thread_id],)
                )
                temp_thread_pool.append(cur_thread)

            return temp_thread_pool

        else:
            for thread_id in range(self.num_threads):
                cur_thread = threading.Thread(
                    target=self.__worker_wrapper, args=(thread_id, self.distributed_work[thread_id],)
                )
                self.__thread_pool.append(cur_thread)

            return None

    def set_worker(self, func):
        """
        Sets the worker, the worker should work on one item from the distributed work.
        Please make sure the worker is thread-safe.
        :param func: Function handle to the worker.
        :return: True/False, indicating if the worker is set correctly
        """
        assert callable(func), "Function provided is not callable!"

        self.__worker = func

        self.create_thread_pool()

        self.__worker_set = True

    def start(self, external_thread_pool=None):
        """
        Starts all threads in the thread pool. Optionally pass in an external thread_pool created from create_thread_pool here.

        :return: True if the worker function is set and threads are started, False otherwise
        """
        if external_thread_pool is None:
            assert self.__worker_set, "Worker function is not set!"

            for t in self.__thread_pool:
                t.start()
        else:
            for t in external_thread_pool:
                t.start()

        return True

    def sync(self, external_thread_pool=None):
        """
        Waits for all threads in the thread pool to finish execution.
        Optionally pass in an external thread_pool created from create_thread_pool here.

        :return: True when all threads have finished execution
        """
        if external_thread_pool is None:
            for t in self.__thread_pool:
                t.join()
        else:
            for t in external_thread_pool:
                t.join()

        if self.verbose:
            print("\nAll threads synchronized.")

        return True

    def get_thread_pool(self):
        """
        Get the created threadpool, if you want to manage it yourself.
        :return: created threadpool
        """
        return self.__thread_pool

    def get_distributed_work(self):
        """
        Get the distributed work, if that's all wanted
        :return: distributed work
        """
        return self.distributed_work

    def get_ret_val(self):
        """
        Retrieves the return values of all threads.

        :return: A list of lists, where each inner list contains the return values of a single thread
        """
        assert self.cache_return_val, "cache_return_val is not set to True!"
        return self.__return_val_cache

    def clear_thread_pool(self):
        """
        Clears the thread pool and resets all settings to defaults.
        This function stops all executing threads.
        """
        self.__stop_event.set()
        self.sync()
        self.__stop_event.clear()

        self.__total_progress = 0
        self.total_work = []
        self.distributed_work = []
        self.num_threads = 0
        self.__total_time_elapsed = 0
        self.__progress = 0
        self.__worker_set = False
        self.cache_return_val = True
        self.verbose = False

    def set_verbose(self, option):
        """
        Sets the verbose flag outside the initialization process.
        :param option: True/False
        :return: None
        """
        self.verbose = option

    def stop_all_threads(self):
        """
        Ask all threads to politely stop executing.
        :return: None
        """
        self.__stop_event.set()


class DynamicThreadPool:
    def __init__(self, work, num_threads=-1, verbose=False, cache_return_val=True):
        assert num_threads != 0, "Num_threads must be -1 or a positive integer!"
        assert num_threads >= -1, "Num_threads must be -1 or a positive integer!"
        assert isinstance(num_threads, int), "Num_threads must be -1 or a positive integer!"

        if num_threads == -1:
            self.num_threads = mp.cpu_count()
        else:
            self.num_threads = num_threads

        self.verbose = verbose

        self.work_queue = queue.Queue()
        self.__total_progress = len(work)

        for w in work:
            self.work_queue.put(w)

        self.__worker_set = False
        self.__thread_pool = []
        self.__stop_event = threading.Event()
        self.__print_lock = threading.Lock()
        self.__total_time = 0
        self.__return_val_cache = {}
        self.cache_return_val = cache_return_val
        self.__progress = 0

    @staticmethod
    def __queue_to_list(q):
        """
        Only call this function after all work is done.
        :param q: queue
        :return: list of the queue
        """
        queue_list = []
        while not q.empty():
            item = q.get()
            queue_list.append(item)
            q.put(item)

        return queue_list

    @staticmethod
    def __worker():
        """
        Placeholder for the worker function that will be set by the user.
        """
        return None

    def __print_progress(self):
        """
        Prints the progress of the thread pool.
        """
        cur_progress = self.__progress

        avg_time_per_task = self.__total_time / (cur_progress if cur_progress != 0 else 1)
        est_remaining_time = avg_time_per_task * (self.__total_progress - cur_progress) / self.num_threads

        print(
            f"\r  DynamicThreadPool Progress Tracker: {cur_progress + 1}/{self.__total_progress}, "
            f"est: {est_remaining_time:.2f}s.",
            end="")

    def __worker_wrapper(self, thread_id):
        """
        Wrapper for the worker function that iterated through the distributed work.
        It also handles error catching and progress tracking.

        :param thread_id: ID of the current thread
        :return: None
        """
        while not self.work_queue.empty():
            start_time = time.time()
            try:
                cur_work = self.work_queue.get()

                if isinstance(cur_work, dict):
                    cur_ret_val = self.__worker(**cur_work)
                else:
                    cur_ret_val = self.__worker(cur_work)

                # create the array if it's the first iteration
                if f"thread {thread_id}" not in self.__return_val_cache:
                    self.__return_val_cache[f"thread {thread_id}"] = []

                # Store the return value of the worker function, if it exists
                if (cur_ret_val is not None) and self.cache_return_val:
                    self.__return_val_cache[f"thread {thread_id}"].append({
                        "param": cur_work,
                        "iteration": thread_id,
                        "return value": cur_ret_val
                    })

                end_time = time.time()
                self.__total_time += (end_time - start_time)

                self.__print_progress()
                self.__progress += 1
                self.work_queue.task_done()
            except Exception as e:
                print(f"An error occurred at thread {thread_id}: {e}")
                self.work_queue.task_done()

    def set_worker(self, func):
        """
        Sets the worker, the worker should work on one item from the distributed work.
        Please make sure the worker is thread-safe.
        :param func: Function handle to the worker.
        :return: True/False, indicating if the worker is set correctly
        """
        assert callable(func), "Function provided is not callable!"

        self.__worker = func

        for thread_id in range(self.num_threads):
            cur_thread = threading.Thread(
                target=self.__worker_wrapper, args=(thread_id,)
            )
            self.__thread_pool.append(cur_thread)

        self.__worker_set = True

    def sync(self):
        for t in self.__thread_pool:
            t.join()
        if self.verbose:
            print("\nAll threads synchronized.")

    def start(self):
        assert self.__worker_set, "Worker function is not set!"
        for t in self.__thread_pool:
            t.start()

    def clear_thread_pool(self):
        while not self.work_queue.empty():
            try:
                self.work_queue.get(False)
            except queue.Empty:
                continue
            self.work_queue.task_done()
        self.__thread_pool = []
        self.__worker_set = False

    def set_verbose(self, option):
        """
        Sets the verbose flag outside the initialization process.
        :param option: True/False
        :return: None
        """
        self.verbose = option

    def stop_all_threads(self):
        """
        Ask all threads to politely stop executing.
        :return: None
        """
        self.__stop_event.set()

    def get_ret_val(self):
        """
        Retrieves the return values of all threads.

        :return: A list of lists, where each inner list contains the return values of a single thread
        """
        assert self.cache_return_val, "cache_return_val is not set to True!"
        return self.__return_val_cache
