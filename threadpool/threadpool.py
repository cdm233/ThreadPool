import threading
import time


class ThreadPool:
    def __init__(self, num_threads, work, tp_verbose=False):
        """
        A basic threadpool that does three things: distribute work, start work, sync.
        Make sure the worker is thread-safe, as this is a ThreadPool, not a monitor.
        :param num_threads: Number of threads to use
        :param work: Total work, this should be a list of all work, e.g.: [{}, {}, ...]
        :param tp_verbose: Verbose, whether to print out stuff or not
        """
        self.num_threads = num_threads
        self.total_work = work

        # printing
        self.verbose = tp_verbose
        self.__progress = 0
        self.__print_lock = threading.Lock()
        self.__total_progress = len(work)

        self.distributed_work = self.distribute_work(work)
        self.__return_val_cache = [[] for _ in range(self.num_threads)]

        if self.verbose:
            print("Work distributed.")

        self.__thread_pool = []

        self.worker_set = False

        if self.verbose:
            print("ThreadPool initialized.")

    def distribute_work(self, total_work):
        """
        Distributes the given work among threads.
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
        pass

    def __print_progress(self, ite_time):
        """
        Prints the progress of the thread pool.

        :param ite_time: The time it took for the last work item to be processed
        """

        # Estimated time to complete all work
        est_time = ite_time * (self.__total_progress - self.__progress) / self.num_threads
        print(f"\r  ThreadPool Progress Tracker: {self.__progress}/{self.__total_progress}, est: {est_time:.2f}s.",
              end="")

    def __worker_wrapper(self, thread_id, work):
        """
        Wrapper for the worker function that iterated through the distributed work.
        It also handles error catching and progress tracking.

        :param thread_id: ID of the current thread
        :param work: List of work for the current thread
        :return: True if no errors occurred, False otherwise
        """

        # List to store the return values of each work item processed by this thread
        temp_ret_val_store = []
        for w in work:
            ite_start = time.time()
            try:
                cur_ret_val = self.__worker(w)
            except:
                print(f"A fatal error occurred at thread {thread_id}.")
                return False

            ite_end = time.time()

            # Store the return value of the worker function, if it exists
            if cur_ret_val is not None:
                temp_ret_val_store.append(cur_ret_val)

            # Print progress update, if verbose mode is enabled
            if self.verbose:
                # Lock the print statement to prevent other threads from interrupting it
                self.__print_lock.acquire()
                self.__progress += 1
                self.__print_progress(ite_end - ite_start)
                self.__print_lock.release()

        self.__return_val_cache[thread_id] = temp_ret_val_store
        return True

    def set_worker(self, func):
        """
        Sets the worker, the worker should work on one item from the distributed work.
        Please make sure the worker is thread-safe.
        :param func: Function handle to the worker.
        :return: True/False, indicating if the worker is set correctly
        """
        self.__worker = func

        for thread_id in range(self.num_threads):
            cur_thread = threading.Thread(
                target=self.__worker_wrapper, args=(thread_id, self.distributed_work[thread_id],)
            )
            self.__thread_pool.append(cur_thread)

        self.worker_set = True

    def start(self):
        """
        Starts all threads in the thread pool.

        :return: True if the worker function is set and threads are started, False otherwise
        """
        if not self.worker_set:
            print("Worker function is not set!")
            return False

        for t in self.__thread_pool:
            t.start()

        return True

    def sync(self):
        """
        Waits for all threads in the thread pool to finish execution.

        :return: True when all threads have finished execution
        """
        for t in self.__thread_pool:
            t.join()

        if self.verbose:
            print("\nAll threads synchronized.")

        return True

    def get_ret_val(self):
        """
        Retrieves the return values of all threads.

        :return: A list of lists, where each inner list contains the return values of a single thread
        """
        return self.__return_val_cache

    def clear_thread_pool(self):
        """
        Clears the thread pool and resets all settings to defaults.
        """
        self.worker_set = False
        self.__total_progress = 0
        self.total_work = []
        self.distributed_work = []
        self.num_threads = 0
