from unittest import TestCase
from tag import MySoup
import re
import os


def paragraphs(s):
    return re.split('\n\s+', s)


_path = lambda s: os.path.join(os.path.dirname(__file__), s)
# TODO: I'm not sure what's going on with the text coming out of the
# html file.
_fix = lambda s: s.encode('latin-1').decode('windows-1252')


class MyTestCase(TestCase):

    def test_get_range(self):
        self.maxDiff = None

        obj = MySoup()
        obj.set_html(_path('filing.html'))
        obj.set_highlights(_path('highlights.json'))

        for d in obj.highlights:
            ranges = d['ranges']
            assert len(ranges) == 1
            df = obj.get_range(ranges[0]['start'], ranges[0]['end'])
            block = df.ix[df.has_text & -df.is_comment]
            text = ''.join(block.text + block['tail']).strip()

            actual = paragraphs(text)
            expected = paragraphs(d['quote'])
            for a, b in zip(actual, expected):
                self.assertEquals(_fix(a), b)
