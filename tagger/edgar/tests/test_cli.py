from unittest import TestCase
from edgar.models import paragraphs, matching_paragraphs, Filing, session
from edgar import cli
import requests
import warnings
import sqlalchemy
import os
from nose.plugins.attrib import attr


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
        self.assertEquals(
            matching_paragraphs(text, last_names),
            paragraphs(text)[1:3]
        )


class TestLoad(TestCase):

    def test_unicode(self):
        folder = '890465/000104746910003386'

        try:
            filing = Filing.get(folder)
            session.delete(filing)
            session.commit()
        except:
            pass

        loader = cli.Loader()
        url = Filing.HTTP_ROOT + folder
        loader.commit_filings([url])
        filing = Filing.get(folder)

        self.assertEquals(type(filing.html), unicode)

        filename = 'a2197676zdef14a.htm'
        url = '/'.join([url, filename])
        response = requests.get(url)

        self.assertTrue(filing.html in response.text)


def test_get_director_names():
    try:
        d = cli._get_director_names()
        assert type(d) == dict
        assert len(d.keys()) == len(cli._get_corpus_folders())
    except sqlalchemy.exc.OperationalError:
        warnings.warn('Cannot test `cli._get_director_names` because `equilar_director_filings` table does not exist.')


def test_get_random_folders():
    n = 10
    try:
        l = cli._get_random_folders(n)
        assert type(l) == list
        assert len(l) == n
    except sqlalchemy.exc.OperationalError:
        warnings.warn('Cannot test `cli._get_random_folders` because `equilar_director_filings` table does not exist.')


def test_write_corpus():
    cli.write_corpus()
    for folder in cli.CORPUS_FOLDERS:
        path = Filing.folder_to_md_path(folder)
        assert os.path.exists(path)
