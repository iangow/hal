import requests
import os
import sqlite3
import pandas as pd
import sys
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

def all_urls(db):
    query = '''
        SELECT url FROM equilar_director_filings
        WHERE url IS NOT NULL
        GROUP BY url
    '''
    with sqlite3.connect(db) as con:
        df = pd.read_sql(query, con)
    return df

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
    # script, db = sys.argv
    db = 'db.sqlite'
    # engine = create_engine('sqlite:///' + db)
    urls = all_urls(db)
    print urls.head()
