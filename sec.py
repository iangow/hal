from bs4 import BeautifulSoup
import pandas as pd
from StringIO import StringIO
from ftplib import FTP

def _join(*args):
    return '/'.join(args)

class Client(object):
    '''
    >>> c = Client()
    >>> c.dir('769397/000076939713000018').shape
    (25, 9)

    >>> c.index_url('769397/000076939713000018')
    '769397/000076939713000018/0000769397-13-000018-index.htm'

    >>> c.def_14a_url('769397/000076939713000018')
    u'769397/000076939713000018/proxydocument.htm'

    >>> c.def_14a_url('1084869/000108486908000022')
    u'1084869/000108486908000022/proxy.txt'

    >>> c.def_14a_url('1364742/000134100410000059') is None
    True
    '''

    def __init__(self):
        self.ftp = FTP('ftp.sec.gov')
        self.ftp.login('anonymous', 'amarder@hbs.edu')
        self.ftp.cwd('/edgar/data/')

    def _open_buffer(self):
        self.buffer = StringIO()

    def _write_buffer(self, s):
        self.buffer.write(s + '\n')

    def _close_buffer(self):
        text = self.buffer.getvalue()
        self.buffer.close()
        return text

    def dir(self, url):
        self._open_buffer()
        self.ftp.dir(url, self._write_buffer)
        text = self._close_buffer()
        return pd.read_fwf(StringIO(text), header=None)

    def index_url(self, url):
        df = self.dir(url)
        filenames = df[8]
        is_index = filenames.map(lambda s: hasattr(s, 'endswith') and s.endswith('index.htm'))
        assert is_index.sum() == 1
        filename = filenames[is_index].values[0]
        return _join(url, filename)

    def file_types(self, url):
        cmd = 'RETR %s' % self.index_url(url)
        self._open_buffer()
        self.ftp.retrlines(cmd, self._write_buffer)
        text = self._close_buffer()
        soup1 = BeautifulSoup(text)
        soup2 = BeautifulSoup(soup1.text)

        get_text = lambda e: e.contents[0].strip()
        get_type = lambda d: get_text(d.type)
        get_filename = lambda d: get_text(d.type.sequence.filename)

        return pd.DataFrame([
            {'Type': get_type(d), 'Document': get_filename(d)}
            for d in soup2.findAll('document')
        ])

    def def_14a_url(self, url):
        df = self.file_types(url)
        df['pdf_file'] = df.Document.map(lambda s: s.endswith('.pdf'))
        flag = 'DEF 14A'
        df['def_14a'] = ((df.Type == flag) | (df.Document == flag)) & -df.pdf_file

        count = df.def_14a.sum()
        assert count in [0, 1], df

        if count == 1:
            filename = df.Document[df.def_14a].values[0]
            return _join(url, filename)
        else:
            return None
