'''
Select a random DEF 14A filing from the database and print the text of
that filing to stdout.
'''

from models import Filing, engine, session
import pandas as pd
import random
import nltk
import re

class Randomizer(object):

    def __init__(self):
        query = 'SELECT id, type FROM filings;'
        self.ids = pd.read_sql(query, engine)

    def get_filing(self):
        df = self.ids
        pk = int(random.choice(df.id[df.type == 'DEF 14A']))
        return session.query(Filing).get(pk)

def write(filing):
    path = filing.csv_path()
    text = filing.text().decode('utf-8')
    sentences = nltk.sent_tokenize(text)
    f = lambda s: re.sub('\s+', ' ', s)
    df = pd.DataFrame({'text': map(f, sentences), 'bio': 0})
    df.to_csv(path, encoding='utf-8', index=False)
    print path

def get_filing(session, folder):
    url = Filing.HTTP_ROOT + folder
    return session.query(Filing).filter(Filing.url==url)[0]

if __name__ == '__main__':
    n = 10
    r = Randomizer()
    for i in range(n):
        write(r.get_filing())
