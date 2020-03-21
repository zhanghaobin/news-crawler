# -*- coding: utf-8 -*-


class DOMTreeError(Exception):
    """
    base exception object for package `dom_tree`
    """


class MultipleNodesError(DOMTreeError):
    """
    more than 1 nodes found rather than expected 1
    """
