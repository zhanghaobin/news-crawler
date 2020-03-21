# -*- coding: utf-8 -*-

from parsers.index_parser import *
from parsers.news_parser import *

from pandas import DataFrame

from typing import Union
from http import HTTPStatus
from requests import request
from requests.exceptions import RequestException, RetryError


class Crawler:

    URL_INDEX = 'https://web.fosu.edu.cn/school-news/page/%d'

    def __init__(self, strict: bool = False,  retry: int = 3, timeout: Union[tuple, float] = None):
        """
        initialization for crawler
        :param strict: should parse DOM nodes in strict mode?
        :param retry: retry times
        :param timeout: seconds timeout for connect & read buffer
        """

        self._retry = retry
        self._timeout = timeout
        self._index_parser = IndexParser(strict)
        self._news_parser = NewsParser(strict)

    def crawl(self, start_page: int = 1, n: int = -1) -> DataFrame:
        """
        start the crawler
        :param start_page: start page for crawl
        :param n: crawl n pages (value `-1` means all pages)
        """

        if start_page < 1:
            raise AttributeError(f'invalid value for start_page: {start_page}')
        if n <= 0 and ~n:
            raise AttributeError(f'invalid value for n: {n}')

        crawled = 0  # crawled page count
        data = DataFrame(columns=['title', 'date', 'author', 'content'])

        while True:
            page = start_page + crawled
            # read & parse index page
            index_meta = self.get_index_meta(page)

            for url in index_meta.newses:
                # print(f'fetching url: {url}')

                # read & parse news detail page
                m = self.get_news_meta(url)
                data.loc[data.shape[0]] = m.meta

            crawled += 1

            if (~n and crawled >= n) or page >= index_meta.last:
                break

        return data

    def get_index_meta(self, page: int = 1) -> IndexMeta:
        """
        get index page & parse as IndexMeta
        :param page: the page number to fetch
        """

        response = self._get(self.URL_INDEX % page)
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f'Expected status code 200, got {response.status_code}')

        return self._index_parser.parse(response.text)

    def get_news_meta(self, url: str) -> NewsMeta:
        """
        get news detail page & parse as NewsMeta
        :param url: the url to fetch
        """

        response = self._get(url)
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f'Expected status code 200, got {response.status_code}')

        return self._news_parser.parse(response.text)

    def _get(self, url: str, **kwargs):
        """
        send a get method request(with retry machining)
        :param url: request url
        :param kwargs: other options(see requests.request)
        """

        return self._request_with_retry('get', url, **kwargs)

    def _request_with_retry(self, method: str, url: str, **kwargs):
        """
        send an request with retry machining
        :param method: request method
        :param url: request url
        :param kwargs: other options (see requests.request)
        """

        exception = None
        for i in range(self._retry):
            try:
                return request(method, url, timeout=self._timeout, **kwargs)
            except RequestException as e:
                exception = e
                continue

        raise RetryError(f'Request failed with retry times: {self._retry}').with_traceback(exception.__traceback__)


if __name__ == '__main__':
    crawler = Crawler()
    print(crawler.crawl(n=1))
