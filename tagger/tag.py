from lxml.html import parse
import json
import pandas as pd
from lxml import etree


def path(tree, e):
    # Note annotator.js does not record implicit [1] index.
    return tree.getpath(e).replace('[1]', '')


def text(e):
    return e.text or ''


def tail(e):
    return e.tail or ''


def has_text(e):
    return len(text(e)) > 0 or len(tail(e)) > 0


def is_comment(e):
    return e.tag is etree.Comment


# https://github.com/aaronsw/html2text/blob/master/html2text.py#L377
# http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/view/head:/bs4/element.py#L1101
PARAGRAPH_TAGS = [
    'blockquote',
    'hr',
    'table',
    'tr',
    'div',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'p',
    'pre',
]


def new_paragraph(e):
    return e.tag in PARAGRAPH_TAGS


class MySoup(object):

    def set_html(self, filename_or_url):
        self.tree = parse(filename_or_url)
        self._set_elements()
        return self

    def _set_elements(self):
        df = pd.DataFrame({'elements': list(self.tree.iter())})
        df['path'] = df.elements.map(lambda e: path(self.tree, e))

        simple_columns = [
            text, tail, has_text, is_comment, new_paragraph
        ]
        for f in simple_columns:
            k = f.__name__
            df[k] = df.elements.map(f)

        df['paragraph'] = df.new_paragraph.cumsum()
        self.elements = df

    def get_range(self, start, end):
        path = self.elements.path
        a = path.map(lambda s: s.endswith(start))
        assert a.sum() == 1
        b = path.map(lambda s: s.endswith(end))
        assert b.sum() == 1
        lower = a.index[a][0]
        # Given endOffset is typically larger than zero we almost
        # always need to grab one extra element.
        upper = b.index[b][0] + 1
        return self.elements.ix[lower:upper]

    def set_highlights(self, path):
        with open(path) as f:
            d = json.load(f)
        self.highlights = d['rows']
        return self
