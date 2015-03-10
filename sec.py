from bs4 import BeautifulSoup
import pandas as pd
from StringIO import StringIO
from io import BytesIO
from ftplib import FTP

def _join(*args):
    return '/'.join(args)

class Client(object):
    '''
    >>> c = Client()
    >>> c.login()
    >>> c.load('769397/000076939713000018')
    >>> c.files.shape
    (25, 9)

    >>> c.index_path
    '769397/000076939713000018/0000769397-13-000018-index.htm'
    
    >>> c.form_path
    u'769397/000076939713000018/proxydocument.htm'
    
    >>> c.load('1084869/000108486908000022')
    >>> c.form_path
    u'1084869/000108486908000022/proxy.txt'
    
    >>> c.load('1364742/000134100410000059')
    >>> c.form_path is None
    True
    
    >>> c.logout()
    '''

    def __init__(self, form='DEF 14A'):
        self.form = form

    def login(self, host='ftp.sec.gov', user='anonymous', passwd='amarder@hbs.edu', cwd='/edgar/data/'):
        self.ftp = FTP(host)
        self.ftp.login(user, passwd)
        self.ftp.cwd(cwd)

    def logout(self):
        self.ftp.quit()

    def _open_buffer(self):
        self.buffer = BytesIO()

    def _write_buffer(self, s):
        self.buffer.write(s)

    def _close_buffer(self):
        text = self.buffer.getvalue()
        self.buffer.close()
        return text

    def retr(self, cmd):
        self._open_buffer()
        self.ftp.retrbinary(cmd, self._write_buffer)
        return self._close_buffer()

    def load(self, folder):
        text = self.retr('LIST %(folder)s' % locals())
        self.files = pd.read_fwf(StringIO(text), header=None)

        df = self.files
        filenames = df[8]
        is_index = filenames.map(lambda s: hasattr(s, 'endswith') and s.endswith('index.htm'))
        assert is_index.sum() == 1
        filename = filenames[is_index].values[0]
        self.index_path = _join(folder, filename)

        cmd = 'RETR %s' % self.index_path
        text = self.retr(cmd)
        soup1 = BeautifulSoup(text)
        soup2 = BeautifulSoup(soup1.text)
        get_text = lambda e: e.contents[0].strip()
        get_type = lambda d: get_text(d.type)
        get_filename = lambda d: get_text(d.type.sequence.filename)
        self.file_types = pd.DataFrame([
            {'Type': get_type(d), 'Document': get_filename(d)}
            for d in soup2.findAll('document')
        ])

        df = self.file_types
        df['pdf_file'] = df.Document.map(lambda s: s.endswith('.pdf'))
        flag = self.form
        df['is_form'] = ((df.Type == flag) | (df.Document == flag)) & -df.pdf_file
        count = df.is_form.sum()
        assert count in [0, 1], df
        if count == 1:
            filename = df.Document[df.is_form].values[0]
            self.form_path = _join(folder, filename)
        else:
            self.form_path = None

        if self.form_path is not None:
            cmd = 'RETR %s' % self.form_path
            self.form_html = self.retr(cmd)
        else:
            self.form_html = None

def get_form(folder):
    c = Client()
    c.login()
    c.load(folder)
    c.logout()
    return c.form_html
