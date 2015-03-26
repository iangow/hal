from sqlalchemy import Column, String, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np
import os
import pandas as pd
import re
import subprocess
from bs4 import BeautifulSoup

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

    def path(self):
        return self.url.replace(self.HTTP_ROOT, '')

    def csv_path(self):
        return os.path.join(
            'corpus',
            re.sub('/', '-', self.path()) + '.csv'
        )

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
        'age',
        'since',
    ]

    def text(self):
        result = clean(self.html.encode('utf-8'))
        assert type(result) == str
        return result

    def _director_last_names(self):
        return map(last_name, self.directors())

    def _markers(self, window=3):
        text = self.text().decode('utf-8')
        pars = paragraphs(text)
        df = pd.DataFrame({
            'bio_word_match': matches(pars, self.BIO_WORDS),
            'text': pars,
        })

        last_names = self._director_last_names()
        for k in last_names:
            assert k not in df
            density = lambda s: float(len(k)) * float(s.lower().count(k.lower())) / float(len(s))
            df[k] = df.text.map(density)
        df['one_name'] = df[last_names].apply(max, 1)

        # Mark 5 paragraphs down from where we see a last name match
        df['name'] = pd.rolling_max(df.one_name, window=window, center=True)

        # Mark 5 paragraphs around where we see a bio word
        df['bio'] = pd.rolling_max(df.bio_word_match, window=window, center=True)

        # Multiply them together and see what we have
        df['mark'] = pd.rolling_mean(df.name * df.bio, window=window, center=True)

        s = np.zeros(len(df.mark))
        for i, flag in enumerate(df.mark):
            if flag:
                if s[i-1]:
                    s[i] = s[i-1]
                else:
                    s[i] = i
        df['group'] = s
        s = df.group.value_counts()
        g = s[s.index != 0].argmax()
        df['flag'] = df.group == g

        return df

    def director_bios(self):
        text = self.text().decode('utf-8')
        matching = matching_paragraphs(text, self._director_last_names())
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
    assert type(stdoutdata) == str, 'subprocess returns a byte string'

    soup = BeautifulSoup(stdoutdata)
    text = soup.get_text(separator=u'\n\n')
    return text.encode('utf-8')

def paragraphs(text):
    return re.split('\n\s+', text.strip())

def matches(paragraphs, tags):
    pattern = '(%s)' % '|'.join(tags)
    return [1 if re.search(pattern, p, re.IGNORECASE) else 0 for p in paragraphs]

def matching_paragraphs(text, last_names):
    pattern = '(%s)' % '|'.join(last_names)
    matching = [p for p in paragraphs(text) if re.search(pattern, p, re.IGNORECASE)]
    return matching

if __name__ == '__main__':
    Base.metadata.create_all(engine)
