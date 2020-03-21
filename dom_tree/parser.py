# -*- coding: utf-8 -*-

from dom_tree.node import *

from re import compile, I


class Parser:
    """
    my custom parser for parsing HTML DOM to be node tree
    there might be lots of bugs and should be used cautiously
    """

    class RegExp:
        """
        static class
        the compiled regular expressions for matching
        """

        DTD = compile(r'\s*<![A-Z][\s\S]*?>\s*', I)  # <!DOCTYPE>

        CDATA = compile(r'\s*<!\[CDATA\[(?P<content>[\s\S]*?)\]\]>\s*', I)  # <![CDATA][>]>

        comment = compile(r'\s*<!--(?P<comment>[\s\S]*?)-->\s*', I)  # <!--comment-->

        text = compile(r'\s*(?P<content>[\s\S]+?(?=\s*<[\s\S]*?>|$))')  # plaintext

        # deprecated
        # tag = compile(r'\s*<\s*(?P<tag>[A-Z]+[A-Z0-9-]*?)'  # tag name
        #               r'(?P<attributes>[\s\S]*?)'  # attributes
        #               r'\s*(?P<closed>/)?\s*>'  # Is it closed?
        #               r'(?(closed)|'  # match below if not closed
        #               r'(?P<children>[\s\S]*(?=(?P<_><\s*/\s*(?P=tag)\s*>))|)'  # children
        #               r'(?(_)(?P<end><\s*/\s*(?P=tag)\s*>)|)'  # end tag (optional in loose mode)
        #               r')\s*', I)  # <tag>children</tag>

        start_tag = compile(r'\s*<\s*(?P<tag>[A-Z]+[A-Z0-9-]*)'  # tag name
                            r'(?P<attributes>[\s\S]*?)'  # attributes
                            r'\s*(?P<closed>/)?\s*>',  # Is it closed?
                            I)  # <tag> | <tag/>

        end_tag = compile(r'\s*<\s*/\s*(?P<tag>[A-Z]+[A-Z0-9-]*)\s*>', I)  # </tag>

        attribute = compile(r'\s*(?P<name>[A-Z]+[A-Z0-9-]*)'  # attribute name
                            r'\s*=\s*'  # `=`
                            r'(?P<quote>["\'])'  # " or '
                            r'(?P<value>.*?)(?P=quote)',  # attribute value
                            I)  # tag node attribute

        _rules = (DTD, CDATA, comment, start_tag, end_tag, text)

        @ classmethod
        def match(cls, content: str):
            """
            try to match content with the rules above
            :param content: the source text to be matched
            """

            for regexp in cls._rules:
                matched = regexp.match(content)

                if matched is not None:
                    return matched

            return None

    def __init__(self, strict: bool = False):
        """
        initialization for parser
        :param strict: in strict mode, the nodes with no close tag will be removed
        """

        self._strict = strict
        self._opened = None  # a stack saving the opened tag nodes

    def parse(self, content: str) -> Node:
        """
        parse content to be a Node object
        :param content: the content to be parsed
        """

        root = Node()
        self._opened = []

        while len(content):
            matched = self.RegExp.match(content)
            if matched is None:
                return root

            pattern = matched.re
            content = content[matched.end():]  # consume the matched part
            parent = self._opened[-1] if len(self._opened) else root

            if pattern is self.RegExp.start_tag:
                tag = matched.group('tag')
                attributes = matched.group('attributes')
                closed = matched.group('closed')
                node = TagNode(tag, self._parse_attributes(attributes), parent)
                parent.children.append(node)

                if not closed:
                    self._opened.append(node)

            elif pattern is self.RegExp.end_tag:
                self._close(matched.group('tag'))

            elif pattern in (self.RegExp.text, self.RegExp.CDATA):
                text = matched.group('content')
                last = parent.children[-1] if len(parent.children) else None

                if isinstance(last, TextNode):
                    last.content += text
                    continue

                parent.children.append(TextNode(text, parent))

        return root

    def _close(self, tag):
        """
        close an opened tag
        :param tag: tag name
        """

        while len(self._opened):
            node = self._opened.pop(-1)
            if node.tag == tag:
                break

            if self._strict:
                # remove unclosed node
                node.parent.children.remove(node)

                # mount the valid node to node.parent
                for child in node.children:
                    child.parent = node.parent
                    node.parent.children.append(child)

    def _parse_attributes(self, attrs: str) -> dict:
        """
        parse tag attributes from string
        :param attrs:
        """

        attributes = {}

        while attrs:
            matched = self.RegExp.attribute.match(attrs)
            if matched is None:
                return attributes

            attributes[matched.group('name')] = matched.group('value')
            attrs = attrs[matched.end():]

        return attributes


if __name__ == '__main__':
    # from requests import get
    # source = get('https://web.fosu.edu.cn/focus-news/30473.html').text

    source = open('./testdata/news-29372.html', 'r', encoding='utf-8').read()
    nodes = [Parser().parse(source)]

    while len(nodes):
        n = nodes.pop(0)
        if n.parent is not None:
            print(f'parent({id(n.parent)})', end=' ')

        if isinstance(n, TextNode):
            print(f'text({id(n)}):', n.text)

        elif isinstance(n, TagNode):
            print(f'tag({id(n)})', n.tag, n.attributes)

        if len(n.children):
            nodes = n.children + nodes
