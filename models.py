from multiprocessing import Pool
import pandas as pd
import sec
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
import sqlite3
import sys
import time

class Filing(Base):

    __tablename__ = 'filings'
    HTTP_ROOT = 'http://www.sec.gov/Archives/edgar/data/'

    id = Column(Integer, primary_key=True)
    url = Column(String(75), unique=True)
    type = Column(String(7), default='')
    html = Column(Text, default='')
    text = Column(Text, default='')
    bios = Column(Text, default='')

def create_filing(url):
    filing = Filing(url=url)
    folder = url.replace(Filing.HTTP_ROOT, '')

    client = sec.Client()
    client.login()
    d = client.load(folder)
    client.logout()

    for k in ['type', 'html']:
        setattr(filing, k, d[k])
    return filing

class Loader(object):

    def __init__(self, db, block_size=10, processes=10):
        self.db = db
        engine = create_engine('sqlite:///' + db)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        self.block_size = block_size
        self.pool = Pool(processes)

    def _new_urls(self):
        unique_urls = '''
            SELECT url FROM equilar_director_filings
            WHERE url IS NOT NULL
            GROUP BY url
        '''
        query = '''
            SELECT url
            FROM (%s)
            LEFT JOIN filings USING (url)
            WHERE filings.id IS NULL;
        ''' % unique_urls

        with sqlite3.connect(self.db) as con:
            df = pd.read_sql(query, con)
        return df.url

    def _blocks(self, l):
        for start in xrange(0, len(l), self.block_size):
            yield l[start:start+self.block_size]

    def load_filings(self):
        urls = self._new_urls()
        n = len(urls) / self.block_size
        for i, block in enumerate(self._blocks(urls)):
            successful = False
            while not successful:
                try:
                    filings = self.pool.map(create_filing, block)
                    successful = True
                except EOFError:
                    print 'I think the program has too many ftp session open. Let us wait thirty seconds and try again.'
                    time.sleep(30)
            self.session.add_all(filings)
            self.session.commit()
            print '\r [%d / %d]' % (i, n)

if __name__ == '__main__':
    script, db = sys.argv
    loader = Loader(db)
    loader.load_filings()
