# -*- coding: utf-8 -*-

from parsers.parser import Meta, Parser
from dom_tree.parser import Parser as DOMTreeParser

from re import compile
from collections.abc import Collection


class IndexMeta(Meta):
    """
    meta object for index page
    """

    @property
    def page(self) -> int:
        return self.meta.get('page', None)

    @property
    def last(self) -> int:
        return self.meta.get('last', None)

    @property
    def newses(self) -> Collection:
        return self.meta.get('newses', None)


class IndexParser(Parser):
    """
    parsers for index page
    """

    def parse(self, content: str) -> IndexMeta:
        root = self._parser.parse(content)

        items = root.filter().cls('list-details').child(0)
        newses = [node.attributes['href'] for node in items]

        page = int(root.filter().cls('current').child(0).node.text)

        last_page = root.filter().cls('extend').nodes[-1].attributes['href'].split('/')[-1]
        last = int(last_page) if last_page else page

        return IndexMeta(page=page, last=last, newses=newses)


if __name__ == '__main__':
    from requests import get

    res = get('https://web.fosu.edu.cn/school-news')
    # print(res.text)
    parser = IndexParser()
    meta = parser.parse(res.text)
    print(meta.meta)
