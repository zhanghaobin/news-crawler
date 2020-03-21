# -*- coding: utf-8 -*-

from collections.abc import Collection


class Node:
    """
    base dom node abject
    """

    def __init__(self, parent=None, children: Collection = None):
        if children is None:
            children = []

        self.parent = parent
        self.children = children

    def filter(self):
        """
        get a NodeFilter object based on self
        """
        from dom_tree.node_filter import NodeFilter

        return NodeFilter(self)


class TextNode(Node):
    """
    text node (with escaped text unescaped)
    """

    escapes = {
        '&nbsp;': ' ',
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&apos;': '\''
    }

    def __init__(self, content: str, parent: Node = None):
        Node.__init__(self, parent)
        self.content = content

    @classmethod
    def escape(cls, text: str):
        for k in cls.escapes:
            text = text.replace(k, cls.escapes[k])
        return text

    @property
    def text(self):
        return self.escape(self.content)


class TagNode(Node):
    """
    base node object for node(s) with tag
    """

    def __init__(self, tag, attributes: dict = None, parent: Node = None, children: Collection = None):

        if attributes is None:
            attributes = {}

        Node.__init__(self, parent, children)
        self.tag = tag
        self.attributes = attributes

    @property
    def id(self):
        return self.attributes.get('id', None)

    @property
    def cls(self):
        return self.attributes.get('class', '').split()
