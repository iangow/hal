from unittest import TestCase
from models import paragraphs, matching_paragraphs

class TestExtract(TestCase):

    def test_paragraphs(self):
        text = '''
        P1

        P2
        '''
        actual = paragraphs(text)
        expected = ['P1', 'P2']
        self.assertEquals(actual, expected)

    def test_matching_paragraphs(self):
        text = '''
        Douglas attended.

        Durst attended.

        Digby was also present.
        '''
        last_names = ['Durst', 'Digby']
        self.assertEquals(matching_paragraphs(text, last_names), paragraphs(text)[1:3])
