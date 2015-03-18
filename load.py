import sec

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

    def _create_filing(self, url):
        if not hasattr(self, 'client'):
            self.client = sec.Client()
            self.client.login()

        filing = Filing(url=url)
        folder = url.replace(Filing.HTTP_ROOT, '')

        d = self.client.load(folder)

        for k in ['type', 'html']:
            setattr(filing, k, d[k])
        return filing

    def load_filings(self):
        urls = self._new_urls()
        n = len(urls) / self.block_size

        for i, block in enumerate(self._blocks(urls)):
            filings = map(self._create_filing, block)
            session.add_all(filings)
            session.commit()
            print '[%d / %d]' % (i, n)

        if len(urls) > 0:
            self.client.logout()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    loader = Loader()
    loader.load_filings()
