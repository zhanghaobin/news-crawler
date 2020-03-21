# -*- coding: utf-8 -*-

from typing import Union
from dom_tree.node import Node, TagNode
from dom_tree.exceptions import MultipleNodesError


class NodeFilter:
    """
    filter for filtering nodes
    """

    def __init__(self, nodes: Union[list, Node]):
        """
        initialization for filter
        :param node: current node
        """

        if isinstance(nodes, Node):
            nodes = [nodes]

        self.nodes = nodes

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return self.nodes.__iter__()

    def __getitem__(self, item):
        return self.nodes[item]

    @property
    def node(self):
        """
        return the only one node
        """
        if len(self.nodes) > 1:
            raise MultipleNodesError(f'Found {len(self.nodes)} nodes in the filter, expected 1')

        return self.nodes[0] if len(self.nodes) else None

    def traverse(self):
        """
        traverse the nodes
        """

        untraversed = self.nodes.copy()

        while len(untraversed):
            node = untraversed.pop(-1)

            if len(node.children):
                untraversed.extend(node.children[::-1])

            yield node

    def attr(self, name: str, value: str):
        """
        filtered by attribute
        :param name: attribute name
        :param value: attribute value
        """

        nodes = []
        for node in self.traverse():
            if not isinstance(node, TagNode) or name not in node.attributes:
                continue

            if node.attributes[name] == value:
                nodes.append(node)

        return NodeFilter(nodes) if len(nodes) else None

    def id(self, idv: str):
        """
        filtered by id
        :param idv: id value
        """

        for node in self.traverse():
            if not isinstance(node, TagNode):
                continue

            if node.id == idv:
                return NodeFilter(node)

        return None

    def cls(self, cls: str):
        """
        filtered by class
        :param cls: class
        """

        nodes = []
        for node in self.traverse():
            if not isinstance(node, TagNode):
                continue

            if cls in node.cls:
                nodes.append(node)

        return NodeFilter(nodes)

    def tag(self, tag: str):
        """
        filtered by tag name
        :param tag: tag name
        """

        nodes = []
        for node in self.traverse():
            if not isinstance(node, TagNode):
                continue

            if node.tag == tag:
                nodes.append(node)

        return NodeFilter(nodes)

    def type(self, t: Node.__class__):
        """
        filtered by node type
        :param t: node type
        """

        nodes = []
        for node in self.traverse():
            if isinstance(node, t):
                nodes.append(node)

        return NodeFilter(nodes)

    def child(self, nth: int):
        """
        filtered by the position of children
        :param nth: child position
        """

        nodes = []
        for node in self.nodes:
            if len(node.children) <= nth:
                continue
            elif nth < 0 and len(node.children) < -nth:
                continue

            nodes.append(node.children[nth])

        return NodeFilter(nodes)


if __name__ == '__main__':
    from dom_tree.parser import Parser
    from dom_tree.node import TextNode

    source = open('./testdata/news-29372.html', 'r', encoding='utf-8').read()
    root = Parser().parse(source)

    n = root.filter().cls('content-item').type(TextNode)
    for i in n:
        print(i.text)
