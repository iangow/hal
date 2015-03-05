import pandas as pd
import re
import sys


class Filing(dict):

    PREFIX = 'http://www.sec.gov/Archives/edgar/data/'

    def __init__(self, folder):
        self.url = self.PREFIX + folder
        self._set_index_url()
        self._set_files()
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

    def _set_files(self):
        '''
        >>> Filing('769397/000076939713000018').files.shape
        (23, 7)
        '''
        self.files = pd.read_html(self.index_url, header=0)[0]

    def _set_def_14a_url(self):
        '''
        >>> Filing('769397/000076939713000018').def_14a_url
        u'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/proxydocument.htm'

        >>> Filing('1084869/000108486908000022').def_14a_url
        u'http://www.sec.gov/Archives/edgar/data/1084869/000108486908000022/proxy.txt'

        >>> Filing('1364742/000134100410000059').is_def_14a
        False
        '''
        df = self.files
        df['pdf_file'] = df.Document.map(lambda s: s.endswith('.pdf'))
        flag = 'DEF 14A'
        df['def_14a'] = ((df.Type == flag) | (df.Document == flag)) & -df.pdf_file

        count = df.def_14a.sum()
        assert count in [0, 1], df
        self.is_def_14a = count == 1

        if self.is_def_14a:
            filename = df.Document[df.def_14a].values[0]
            self.def_14a_url = '/'.join([self.url, filename])
        else:
            # TODO: Better logging system.
            # sys.stderr.write(str(df.Type.values))
            # sys.stderr.write('\n')
            pass
