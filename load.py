import sec
from models import Filing, engine, session
import pandas as pd

class Loader(object):

    def __init__(self, block_size=10, processes=10):
        self.block_size = block_size
        # self.pool = Pool(processes)

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
        df = pd.read_sql(query, engine)
        return df.url

    def _blocks(self, l):
        for start in xrange(0, len(l), self.block_size):
            yield l[start:start+self.block_size]

    def create_filing(self, url):
        if not hasattr(self, 'client'):
            self.client = sec.Client()
            self.client.login()

        filing = Filing(url=url)
        folder = url.replace(Filing.HTTP_ROOT, '')

        d = self.client.load(folder)

        for k in ['type', 'html']:
            setattr(filing, k, d[k])
        return filing

    def commit_filings(self, urls):
        filings = map(self.create_filing, urls)
        session.add_all(filings)
        session.commit()

    def load_filings(self):
        urls = self._new_urls()
        n = len(urls) / self.block_size

        for i, block in enumerate(self._blocks(urls)):
            self.commit_filings(block)
            print '[%d / %d]' % (i, n)

        if len(urls) > 0:
            self.client.logout()

if __name__ == '__main__':
    
    loader = Loader()
    loader.load_filings()
