# -*- coding: utf-8 -*-

from dom_tree.node import TextNode
from parsers.parser import Meta, Parser

from re import compile
from datetime import date
from functools import reduce


class NewsMeta(Meta):
    """
    meta object for news detail page
    """

    @property
    def title(self) -> str:
        return self.meta.get('title', None)

    @property
    def date(self) -> date:
        dt = self.meta.get('date', None)

        if not isinstance(dt, date):
            dt = date.fromisoformat(dt)

        return dt

    @property
    def content(self) -> str:
        return self.meta.get('content', None)

    @property
    def author(self) -> str:
        return self.meta.get('author', None)


class NewsParser(Parser):
    """
    parsers for news detail page
    """

    _regexp_author = compile(r'(?P<content>[\s\S]*)((?P<b1>\()|(?P<b2>（))'  # bracket
                             r'(?P<author>.*?)'  # author
                             r'(?(b1)\)|(?(b2)）|(?!)))\s*$')

    def parse(self, content: str) -> NewsMeta:
        root = self._parser.parse(content)
        header = root.filter().cls('content-title')
        title = header.tag('h1').child(0).node.text
        time = header.cls('vartime').child(0).node.text[-10:]
        texts = root.filter().cls('content-item').type(TextNode)
        content = reduce(lambda r, s: r + s.text.strip(), texts, '')

        author = None
        matched = self._regexp_author.match(content)

        if matched is not None:
            author = matched.group('author')
            content = content[:matched.end('content')]

        return NewsMeta(title=title, author=author, date=time, content=content)


if __name__ == '__main__':
    from requests import get

    res = get('https://web.fosu.edu.cn/focus-news/30473.html')
    # print(res.text)

    parser = NewsParser()
    meta = parser.parse(res.text)
    print(meta.meta)
