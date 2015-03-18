from fuzzywuzzy import fuzz
from multiprocessing import Pool
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from unittest import TestCase
import codecs
import glob
import os
import pandas as pd
import re
import subprocess

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Filing(Base):

    __tablename__ = 'filings'
    HTTP_ROOT = 'http://www.sec.gov/Archives/edgar/data/'

    id = Column(Integer, primary_key=True)
    url = Column(String(75), unique=True)
    type = Column(String(7), default='')
    html = Column(Text, default='')
    text = Column(Text, default='')
    bios = Column(Text, default='')

    def directors(self):
        query = (
            'SELECT director FROM equilar_director_filings WHERE url="%s";' % self.url
            )
        df = pd.read_sql(query, engine)
        return list(df.director)

    BIO_WORDS = [
        'served',
        'degree',
        'University',
        'holds',
        'College',
        'MBA',
    ]

    def director_bios(self):
        last_names = map(last_name, self.directors())
        text = clean(self.html.encode('utf-8')).decode('utf-8')
        matching = matching_paragraphs(text, last_names)
        rejoined = '\n\n'.join(matching)
        matching = matching_paragraphs(rejoined, self.BIO_WORDS)
        # TODO: these are byte strings at the moment
        return u'\n\n'.join(matching)

    @classmethod
    def get(cls, folder):
        url = cls.HTTP_ROOT + folder
        qs = session.query(cls).filter(cls.url == url)
        l = list(qs)
        assert len(l) == 1
        return l[0]

last_name = lambda s: s.split(',')[0]

def clean(html):
    '''
    >>> print clean('<b>heading</b>').strip()
    **heading**
    '''
    assert type(html) == str, 'subprocess needs a byte string'
    
    args = ['pandoc', '--from=html', '--to=markdown_strict']
    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    stdoutdata, stderrdata = p.communicate(html)
    return stdoutdata

def paragraphs(text):
    return re.split('\n\s+', text.strip())

def matching_paragraphs(text, last_names):
    pattern = '(%s)' % '|'.join(last_names)
    matching = [p for p in paragraphs(text) if re.search(pattern, p, re.IGNORECASE)]
    return matching

target_md = lambda s: re.sub(Filing.HTTP_ROOT, '', s).replace('/', '-') + '.md'
target_path = lambda s: os.path.join('targets', target_md(s))
path2folder = lambda s: re.sub('[^-0-9]', '', s).replace('-', '/')

def benchmark(folder):
    path = target_path(folder)
    with codecs.open(path, encoding='utf-8') as f:
        target = f.read()

    f = Filing.get(folder)
    actual = f.director_bios()

    d = {
        'ratio': fuzz.ratio(actual, target),
        'folder': folder,
    }
    return d

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

if __name__ == '__main__':
    paths = glob.glob('targets/*.md')
    folders = map(path2folder, paths)
    pool = Pool(len(folders))
    l = pool.map(benchmark, folders)
    df = pd.DataFrame(l)
    print df.sort('ratio')
