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

class Randomizer(object):

    def __init__(self, db):
        query = 'SELECT id, type FROM filings;'
        engine = create_engine('sqlite:///' + db)
        Session = sessionmaker(bind=engine)
        self.ids = pd.read_sql(query, engine)
        self.session = Session()

    def get_filing(self):
        df = self.ids
        pk = int(random.choice(df.id[df.type == 'DEF 14A']))
        return self.session.query(Filing).get(pk)

def clean(html):
    '''
    >>> print clean('<b>heading</b>').strip()
    **heading**
    '''
    args = ['pandoc', '--from=html', '--to=markdown']
    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    stdoutdata, stderrdata = p.communicate(html)
    return stdoutdata

def write(filing):
    filename = re.sub(Filing.HTTP_ROOT, '', filing.url).replace('/', '-') + '.md'
    path = os.path.join('targets', filename)
    with open(path, 'w') as f:
        f.write(clean(filing.html))
    print path

if __name__ == '__main__':
    n = 8
    r = Randomizer(db='db.sqlite')
    for i in range(n):
        write(r.get_filing())
