# -*- coding: utf-8 -*-

from dom_tree.parser import Parser as DOMTreeParser


class Meta:
    """
    base meta object
    """

    def __init__(self, **kwargs):
        self.meta = kwargs


class Parser:
    """
    base parsers interface
    """

    def __init__(self, strict: bool = False):
        self._strict = strict  # should parse in strict mode?
        self._parser = DOMTreeParser(strict)

    def parse(self, content: str) -> Meta:
        """
        perform parse action
        :param content: the raw html page content
        """
