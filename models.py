import os
from multiprocessing import Pool
import pandas as pd
import requests
import sec
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
import sqlite3
import sys

class Filing(Base):

    __tablename__ = 'filings'

    id = Column(Integer, primary_key=True)
    url = Column(String(75), unique=True)
    def_14a_url = Column(String(150), nullable=True, default='') # TODO: Test NULL != ''
    html = Column(Text, default='')
    text = Column(Text, default='')
    bios = Column(Text, default='')

    def download(self):
        path = self.local_path()
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        response = requests.get(self.remote_url)
        with open(path, 'w') as f:
            f.write(response.text)
        assert self.downloaded()

    def read(self):
        with open(self.local_path()) as f:
            return f.read()

class Loader(object):

    def __init__(self, db, block_size=1000, processes=32):
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
        return df

    def load_urls(self):
        df = self._new_urls()
        for i, url in enumerate(df.url.values):
            f = Filing(url=url)
            self.session.add(f)
            if i % self.block_size == 0:
                self.session.flush()
        self.session.commit()

    def set_def_14a_urls(self):
        qs = self.session.query(Filing).filter(Filing.def_14a_url=='')
        filings = list(qs)
        urls = [f.url for f in filings]
        def_14a_urls = self.pool.map(sec.def_14a_url, urls)
        
        for f, def_14a in zip(filings, def_14a_urls):
            f.def_14a_url = def_14a
            self.session.add(f)
        self.session.commit()

def load(folder):
    folder_url = '/'.join([Filing.REMOTE_ROOT, folder])
    matches = list(Filing.objects.filter(remote_url__startswith=folder_url))
    count = len(matches)
    assert count in [0, 1]
    if count == 1:
        return matches[0]

    filing = Filing(folder)
    if filing.is_def_14a:
        return Filing.objects.create(remote_url=filing.def_14a_url)
    else:
        return filing

if __name__ == '__main__':
    script, db = sys.argv
    loader = Loader(db)
    # loader.load_urls()
    loader.set_def_14a_urls()
