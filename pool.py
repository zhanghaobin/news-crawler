# -*- coding: utf-8 -*-

from threading import Thread
from queue import Queue, Empty


class ThreadPool:
    """
    a thread pool
    """

    class Worker(Thread):
        """
        worker thread
        """

        def __init__(self, live_timeout: float = None, pool=None, **kwargs):
            Thread.__init__(self, **kwargs)
            self._pool = pool
            self._timeout = live_timeout

        def run(self):

            while True:
                if (self._pool.state == ThreadPool.STATE_TERMINATED or
                        (self._pool.state == ThreadPool.STATE_STOP and self._pool.tasks.empty())):
                    break

                try:
                    # get & run task
                    self._pool.tasks.get(timeout=self._timeout)()
                except Empty:
                    self._pool.workers.remove(self)
                    break
                except:
                    self._pool.workers.remove(self)
                    raise

    STATE_RUNNING = 0
    STATE_STOP = 1
    STATE_TERMINATED = 2

    def __init__(self, core_worker_num: int = 2, max_worker_num: int = 4,
                 max_task_num: int = 0, live_timeout: float = None,
                 qctr: Queue.__class__ = Queue):
        """
        initialization for ThreadPool
        :param core_worker_num: the number of core worker threads (will be created immediately when a new task arrived)
        :param max_worker_num: max number of worker threads
        :param max_task_num: max num of tasks could be accepted
        :param live_timeout: time to live for worker thread when no task need to be processed (seconds)
        :param qctr: Queue constructor for task queue
        """

        self.workers = []
        self.state = self.STATE_RUNNING
        self._timeout = live_timeout
        self.tasks = qctr(max_task_num)
        self._core_worker_num = core_worker_num
        self._max_worker_num = max_worker_num

    def put(self, task: callable, block: bool = True, timeout: float = None):
        """
        put a task into task queue
        :param task: target task
        :param block: see Queue.put()
        :param timeout: see Queue.put()
        """

        if self.state != self.STATE_RUNNING:
            raise RuntimeError('Task rejected (thread pool not running)')

        worker_num = len(self.workers)
        if worker_num < self._core_worker_num or (not self.tasks.empty() and worker_num < self._max_worker_num):
            worker = ThreadPool.Worker(self._timeout, self)
            worker.start()
            self.workers.append(worker)

        return self.tasks.put(task, block, timeout)

    def stop(self):
        """
        stop the thread pool (wait for tasks finished)
        """

        self.state = self.STATE_STOP
        for i in range(len(self.workers) - 1, -1, -1):
            self.workers[i].join()
            del self.workers[i]

    def terminate(self):
        """
        terminate the thread pool
        """

        self.state = self.STATE_TERMINATED
        for i in range(len(self.workers) - 1, -1, -1):
            del self.workers[i]
