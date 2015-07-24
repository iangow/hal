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

    def set_highlights(self, path):
        with open(path) as f:
            d = json.load(f)
        self.highlights = d['rows']
        return self

    def _iter_depth_first(self, e):
        '''
        Iterate through the text contained in this element and its
        children, yielding (xpath, text) pairs as we go along.
        '''
        e_path = path(self.tree, e)

        if e.text and not is_comment(e):
            yield e_path, e.text

        for c in e.getchildren():
            for c_path, c_text in self._iter_depth_first(c):
                yield c_path, c_text

        if e.tail:
            yield e_path, e.tail

    def get_range(self, start, end, startOffset, endOffset):
        my_iter = self._iter_depth_first(self.tree.getroot())

        started = False
        ended = False

        nchars_past_end = 0
        result = ''

        for path, text in my_iter:
            if path.endswith(start):
                started = True
            if path.endswith(end):
                ended = True

            if started:
                result += text
            if ended:
                nchars_past_end += len(text)

            if nchars_past_end >= endOffset:
                break

        cutoff = nchars_past_end - endOffset
        return result[startOffset:(len(result) - cutoff)]
