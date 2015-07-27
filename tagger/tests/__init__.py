from unittest import TestCase
from ..tag import MySoup
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

        data = [
            {
                'html': 'data_filing.html',
                'json': 'data_highlights.json',
            },
            {
                'html': 'data_text_filing.html',
                'json': 'data_text_highlights.json',
            }
        ]
        for d in data:
            self._test_get_range(d)

    def _test_get_range(self, filenames):
        obj = MySoup()
        obj.set_html(_path(filenames['html']))
        obj.set_highlights(_path(filenames['json']))

        for d in obj.highlights:
            ranges = d['ranges']
            assert len(ranges) == 1
            actual = obj.get_range(**ranges[0])
            expected = d['quote']
            self.assertEquals(_fix(actual), expected)
