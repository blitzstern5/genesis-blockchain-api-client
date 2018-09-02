import sys
IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    from Queue import Queue
else:
    from queue import Queue

from threading import Thread

workers_results = []

class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks, **kwargs):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.print_exception = kwargs.get('print_exception', False)
        self.start()

    def run(self):
        global workers_results
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                if self.print_exception:
                    print("An exception happened in this thread: %s" % e)
                workers_results.append({"func": func, "args": args,
                    "kargs": kargs, "error": e})
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()
                workers_results.append({"func": func, "args": args,
                    "kargs": kargs})


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads, **kwargs):
        self.tasks = Queue(num_threads)
        self.print_exceptions = kwargs.get('print_exceptions', False)
        for _ in range(num_threads):
            Worker(self.tasks, print_exception=self.print_exceptions)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            if type(args) == tuple:
                self.add_task(func, *args)
            else:
                self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()

    def get_results(self):
        return workers_results

    def print_results(self):
        for result in self.get_results():
            print("result: %s" % result)

    def get_success_results(self):
        results = []
        for result in self.get_results():
            if "error" not in result:
                results.append(result)
        return results

    def get_error_results(self):
        results = []
        for result in self.get_results():
            if "error" in result:
                results.append(result)
        return results

    def results_contain_errors(self):
        for result in self.get_results():
            if "error" in result:
                return True
        return False

    def print_success_results(self):
        for result in self.get_success_results():
            print(result)

    def print_error_results(self):
        for result in self.get_error_results():
            print("result: %s" % result)
            print("")

if __name__ == "__main__":
    import random
    import string
    from random import randrange, randint
    from time import sleep

    def generate_random_name():
        name = []
        for _ in range(1, 30):
            sym = random.choice(string.ascii_lowercase)
            name.append(sym)
            return "".join(name)

    class TestException(Exception):
        pass

    # Function to be executed in a thread
    def wait_delay(d):
        print("sleeping for (%d)sec" % d)
        sleep(d)
        if randint(0, 3) == 0:
            print("generating exception")
            raise TestException("This is a test exception")

    # Generate random delays
    num = 10
    delays = [randrange(3, 7) for i in range(num)]

    # Instantiate a thread pool with 5 worker threads
    pool = ThreadPool(5, print_exceptions=False)
    pool.map(wait_delay, delays)
    pool.wait_completion()
    print("Number of success results: %d" % len(pool.get_error_results()))
    print("Number of error results: %d" % len(pool.get_success_results()))
    if len(pool.get_error_results()) == 0:
        print("Total result: OK")
    else:
        print("Total result: ERROR")
        pool.print_error_results()


