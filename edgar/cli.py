'''
A command line interface for setting things up.

A helper script designed to help build a corpus of filings.

Given a table of director-filing pairs already exists in the
database. This script identifies the filings that have not been
downloaded from the SEC yet and downloads them, saving the data to the
database.
'''

from edgar.models import engine, Filing, clean, session
from sec_ftp import Client
import json
import os
import pandas as pd
import random
import sec_ftp
import sys


def _get_corpus_folders():
    with open('corpus/corpus.txt') as f:
        return f.read().split()


def _get_director_names():
    # Director names are formatted "last, first"
    query = 'SELECT url, director FROM equilar_director_filings;'
    director_filings = pd.read_sql(query, engine)
    folders = _get_corpus_folders()

    filings = pd.DataFrame({
        'folder': folders
    })
    filings['url'] = filings.folder.map(lambda s: Filing.HTTP_ROOT + s)

    # TODO: It's interesting that some names are repeated multiple
    #       times for the same filing.
    merged = filings.merge(director_filings, how='left', on='url')
    pairs = [
        (folder, sorted(list(df.director.unique())))
        for folder, df in merged.groupby('folder')
        ]
    return dict(pairs)


def print_director_names():
    '''
    A helper script for pulling director names from the database and
    printing them to the screen. This is used to create
    /corpus/director.json
    '''
    d = _get_director_names()
    print json.dumps(d, indent=2)


def _get_random_folders(n):
    '''
    This is useful when we want to create a list of random
    filings. This is the function I used to generate corpus.txt.
    '''
    assert type(n) == int
    query = 'SELECT url FROM equilar_director_filings GROUP BY url;'
    all_urls = list(pd.read_sql(query, engine).url)
    urls = []
    while len(urls) < n:
        url = random.choice(all_urls)
        if url not in urls:
            urls.append(url)
    return map(lambda s: s.replace(Filing.HTTP_ROOT, ''), urls)


def print_random_folders(n):
    folders = _get_random_folders(int(n))
    print '\n'.join(folders)


with open(os.path.join('corpus', 'corpus.txt')) as f:
    CORPUS_FOLDERS = [l.strip() for l in f]


def write_corpus():
    paths = [Filing.folder_to_md_path(folder) for folder in CORPUS_FOLDERS]
    not_written = [
        CORPUS_FOLDERS[i]
        for i, p in enumerate(paths)
        if not os.path.exists(p)
    ]
    dictionaries = _load(not_written)
    map(_write, dictionaries)


def _load(folders):
    c = Client()
    c.login()
    dictionaries = [c.load(folder) for folder in folders]
    c.logout()
    return dictionaries


def _write(d):
    filing = Filing(
        url=Filing.HTTP_ROOT + d['folder']
    )
    path = filing.md_path()
    print 'Writing:', path
    text = d['text']
    if not d['text_file']:
        text = clean(text)
    with open(path, 'w') as f:
        f.write(text)


class Loader(object):

    UNIQUE_URLS = '''
        SELECT url FROM equilar_director_filings
        WHERE url IS NOT NULL
        GROUP BY url
    '''

    NEW_URLS = '''
        SELECT url
        FROM (%s)
        LEFT JOIN filings USING (url)
        WHERE filings.id IS NULL;
    ''' % UNIQUE_URLS

    def __init__(self, block_size=10, processes=10):
        self.block_size = block_size
        # self.pool = Pool(processes)

    def _urls(self, query):
        df = pd.read_sql(query, engine)
        return df.url

    def all_urls(self):
        return self._urls(self.UNIQUE_URLS)

    def _blocks(self, l):
        for start in xrange(0, len(l), self.block_size):
            yield l[start:start+self.block_size]

    def create_filing(self, url):
        if not hasattr(self, 'client'):
            self.client = sec_ftp.Client()
            self.client.login()

        try:
            filing = Filing.get(url)
        except:
            filing = Filing(url=url)
        folder = url.replace(Filing.HTTP_ROOT, '')

        d = self.client.load(folder)

        filing.type = d['type']
        filing.html = d['text']

        return filing

    def commit_filings(self, urls):
        filings = map(self.create_filing, urls)
        session.add_all(filings)
        session.commit()
        return filings

    def load_filings(self):
        urls = self._urls(self.NEW_URLS)
        n = len(urls) / self.block_size

        for i, block in enumerate(self._blocks(urls)):
            self.commit_filings(block)
            print '[%d / %d]' % (i, n)

        if len(urls) > 0:
            self.client.logout()


def load_filings():
    loader = Loader()
    loader.load_filings()

    # post condition
    urls = loader._urls(loader.NEW_URLS)
    assert len(urls) == 0


if __name__ == '__main__':
    this_path = sys.argv[0]
    function_name = sys.argv[1]
    args = sys.argv[2:len(sys.argv)]

    f = locals()[function_name]
    f(*args)
