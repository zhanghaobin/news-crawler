# -*- coding: utf-8 -*-

from crawler import Crawler
from pool import ThreadPool
from queue import Queue
from warnings import warn
from os import makedirs, remove, listdir
from os.path import join, exists, isfile


class CrawlTask:
    """
    run crawl task with multiple threads
    """

    DATA_PATH = './data'
    TEMP_PATH = join(DATA_PATH, 'temp')

    def __init__(self, start_page: int = 1, n: int = -1,
                 core_worker_num: int = 2, max_worker_num: int = 4,
                 crawl_unit: int = 10):
        """
        initialization for CrawTask
        :param start_page: the start page to crawl
        :param n: crawl n pages (value `-1` means all pages)
        :param core_worker_num: see pool.ThreadPool
        :param max_worker_num: see pool.ThreadPool
        :param crawl_unit: the page unit to crawl for a single task
        """

        if not exists(self.TEMP_PATH):
            makedirs(self.TEMP_PATH)
        else:
            self._clean()

        # ensures each thread run with one crawler
        self._crawlers = Queue(maxsize=max_worker_num)
        for i in range(max_worker_num):
            # initialize max_worker_num crawlers
            self._crawlers.put(Crawler())

        self._pool = ThreadPool(core_worker_num, max_worker_num)

        self._crawl_all = not ~n
        self._start = start_page
        self._crawl_unit = crawl_unit
        crawler = self._crawlers.get()
        self._pages = crawler.get_index_meta().last
        self._crawlers.put(crawler)

        if start_page > self._pages:
            raise AttributeError(f'no enough page to crawl, at most {self._pages}')
        if ~n and start_page + n - 1 > self._pages:
            n = self._pages - start_page + 1
            warn(f'no enough page to crawl, n was set to {n}')

        self._n = self._pages - self._start + 1 if self._crawl_all else n

    def start(self):
        """
        start crawl task
        """

        for i in range(self._start, self._start + self._n, self._crawl_unit):
            self._pool.put(self._task(i))

        self._pool.stop()  # wait for all tasks finished
        print('merging files...')
        self._merge()  # merge temp files
        print('done!')

    def _task(self, start_page: int) -> callable:
        """
        single crawl task
        :param start_page: start page to crawl
        """

        def executor():
            end_page = start_page + n - 1 if ~n else ''

            try:
                print(f'[{start_page}-{end_page}]: crawling...')
                crawler = self._crawlers.get()  # get a crawler from pool
                data = crawler.crawl(start_page, n)
                self._crawlers.put(crawler)  # put the crawler back to pool
                data.to_csv(join(self.TEMP_PATH, f'{start_page}-{end_page}.csv'),
                            header=start_page == self._start, index=False)
                print(f'[{start_page}-{end_page}]: crawl successfully!')
            except Exception as e:
                warn(f'[{start_page}-{end_page}]: crawl failed!\n{e}', source=e)

        n = self._crawl_unit
        if start_page + self._crawl_unit > self._pages:
            n = self._pages - start_page if not self._crawl_all else -1

        return executor

    def _clean(self):
        """
        clean the temp directory
        """

        for n in listdir(self.TEMP_PATH):
            path = join(self.TEMP_PATH, n)

            if isfile(path):
                remove(path)

    def _merge(self):
        """
        merge the crawled csv files
        """

        files = listdir(self.TEMP_PATH)
        files.sort()  # sort by page number ASC
        f = open(join(self.DATA_PATH, 'data.csv'), 'w', encoding='utf-8')

        for n in files:
            path = join(self.TEMP_PATH, n)
            if isfile(path):
                f.write(open(path, 'r', encoding='utf-8').read())

        f.close()


if __name__ == '__main__':
    CrawlTask(core_worker_num=4, max_worker_num=16).start()

    from pandas import read_csv
    print(read_csv(join(CrawlTask.DATA_PATH, 'data.csv')))
