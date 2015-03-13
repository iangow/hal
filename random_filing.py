'''
Select a random DEF 14A filing from the database and print the text of
that filing to stdout.
'''
import pandas as pd
import random
from sqlalchemy import create_engine
from models import Filing
from sqlalchemy.orm import sessionmaker
import subprocess

db = 'db.sqlite'

def random_filing():
    query = 'SELECT id, type FROM filings;'
    engine = create_engine('sqlite:///' + db)
    Session = sessionmaker(bind=engine)
    session = Session()
    df = pd.read_sql(query, engine)

    pk = int(random.choice(df.id[df.type == 'DEF 14A']))
    filing = session.query(Filing).get(pk)


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
