import pandas as pd


class Filing(dict):

    PREFIX = 'http://www.sec.gov/Archives/edgar/data/'

    def __init__(self, folder):
        self.url = self.PREFIX + folder
        self._set_index_url()
        self._set_doc()
        self._set_def_14a_url()

    def _set_index_url(self):
        '''
        >>> Filing('769397/000076939713000018').index_url
        u'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/0000769397-13-000018-index.htm'
        '''
        df = pd.read_html(self.url, header=0)[0]
        df['is_index'] = df.Name.map(lambda s: hasattr(s, 'endswith') and s.endswith('index.htm'))
        assert df.is_index.sum() == 1
        filename = df.Name[df.is_index].values[0]
        self.index_url = '/'.join([self.url, filename])

    def _set_doc(self):
        '''
        Returns the html document submitted to edgar. Ignores images and
        the complete submission file.

        >>> Filing('769397/000076939713000018')._doc
        {u'Document': u'proxydocument.htm', u'Type': u'DEF 14A', u'Description': u'DEF 14A', u'Seq': 1.0, u'Size': 2205821}

        >>> Filing('54991/000095015202009613')._doc
        {u'Document': u'l97695bdef14a.htm', u'Type': u'DEF 14A', u'Description': u'KEITHLEY INSTRUMENTS DEFINITIVE PROXY', u'Seq': 1.0, u'Size': 187133}
        '''
        exclude = {
            'Type': ['GRAPHIC', 'EX-99', 'EX-99.1'],
            'Description': ['Complete submission text file']
        }
        df = pd.read_html(self.index_url, header=0)[0]
        for k, l in exclude.items():
            for v in l:
                drop = df[k] == v
                df = df[-drop]

        # Drop pdf files
        pdf_file = df.Document.map(lambda s: s.endswith('.pdf'))
        df = df[-pdf_file]

        assert df.shape[0] == 1, df
        self._doc = df.ix[0].to_dict()

    def _set_def_14a_url(self):
        '''
        >>> Filing('769397/000076939713000018').def_14a_url
        u'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/proxydocument.htm'

        >>> Filing('1084869/000108486908000022').def_14a_url
        u'http://www.sec.gov/Archives/edgar/data/1084869/000108486908000022/proxy.txt'
        '''
        d = self._doc

        self.is_def_14a = d['Type'] == 'DEF 14A' or d['Description'] == 'DEF 14A'

        if self.is_def_14a:
            self.def_14a_url = '/'.join([self.url, d['Document']])
        else:
            # TODO: Betting logging system.
            print d
