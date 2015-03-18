'''
Select a random DEF 14A filing from the database and print the text of
that filing to stdout.
'''

from models import Filing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import pandas as pd
import random
import re
import subprocess

def get_engine_and_session(db):
    engine = create_engine('sqlite:///' + db)
    Session = sessionmaker(bind=engine)
    session = Session()
    return engine, session

class Randomizer(object):

    def __init__(self, db):
        query = 'SELECT id, type FROM filings;'
        e, s = get_engine_and_session(db)
        self.ids = pd.read_sql(query, e)
        self.session = s

    def get_filing(self):
        df = self.ids
        pk = int(random.choice(df.id[df.type == 'DEF 14A']))
        return self.session.query(Filing).get(pk)

def write(filing):
    path = target_path(filing.url)
    with open(path, 'w') as f:
        f.write(clean(filing.html))
    print path

def get_filing(session, folder):
    url = Filing.HTTP_ROOT + folder
    return session.query(Filing).filter(Filing.url==url)[0]

if __name__ == '__main__':
    n = 10
    r = Randomizer(db='db.sqlite')
    for i in range(n):
        write(r.get_filing())
