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
import subprocess

def random_filing(db):
    query = 'SELECT id, type FROM filings;'
    engine = create_engine('sqlite:///' + db)
    Session = sessionmaker(bind=engine)
    session = Session()
    df = pd.read_sql(query, engine)
    pk = int(random.choice(df.id[df.type == 'DEF 14A']))
    return session.query(Filing).get(pk)

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

db = 'db.sqlite'
filing = random_filing(db)
filename = re.sub(Filing.HTTP_ROOT, '', filing.url).replace('/', '-') + '.md'
path = os.path.join('targets', filename)
with open(path, 'w') as f:
    f.write(clean(filing.html))
