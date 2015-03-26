from unittest import TestCase
from models import paragraphs, matching_paragraphs, Filing
from load import Loader
import requests

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

class TestLoad(TestCase):

    def test_unicode(self):
        folder = '890465/000104746910003386'

        url = Filing.HTTP_ROOT + folder
        loader = Loader()

        try:
            filing = Filing.get(folder)
        except:
            loader.commit_filings([url])
        finally:
            filing = Filing.get(folder)
        
        self.assertEquals(type(filing.html), unicode)
        
        filename = 'a2197676zdef14a.htm'
        url = '/'.join([url, filename])
        response = requests.get(url)

        self.assertEquals(filing.html, response.text)
