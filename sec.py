from bs4 import BeautifulSoup
import pandas as pd
from StringIO import StringIO
from io import BytesIO
from ftplib import FTP
import re

def _join(*args):
    return '/'.join(args)

class Client(object):
    '''
    >>> c = Client()
    >>> c.login()
    >>> d = c.load('769397/000076939713000018')

    >>> d['index_path']
    '769397/000076939713000018/0000769397-13-000018-index.htm'
    
    >>> d['form_path']
    u'769397/000076939713000018/proxydocument.htm'
    
    >>> c.load('1084869/000108486908000022')['form_path']
    u'1084869/000108486908000022/proxy.txt'
    
    >>> c.load('1364742/000134100410000059')['type']
    u'DEF 14C'

    >>> c.load('1001871/000115752306006856')['form_path']
    u'1001871/000115752306006856/a5187774.txt'

    >>> c.load('1100663/000119312509185679')['form_path']
    u'1100663/000119312509185679/ddef14a.htm'

    >>> c.logout()
    '''

    TYPES = ['DEF 14A', 'DEF 14C']

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
        self.filing = {'folder': folder}
        self._load_dir()
        self._load_index()
        self._load_form()
        return self.filing

    def _load_dir(self):
        text = self.retr('LIST %(folder)s' % self.filing)
        df = pd.read_fwf(StringIO(text), header=None)
        filenames = df[8]
        is_index = filenames.map(lambda s: hasattr(s, 'endswith') and s.endswith('index.htm'))
        assert is_index.sum() == 1
        filename = filenames[is_index].values[0]
        self.filing['index_path'] = _join(self.filing['folder'], filename)

    def _lowercase_tags(self, text):
        return re.sub('<[^>]*?>', lambda m: m.group(0).lower(), text)
        
    def _get_document_info(self):
        cmd = 'RETR %(index_path)s' % self.filing
        text = self.retr(cmd)
        soup1 = BeautifulSoup(text)
        sgml = self._lowercase_tags(soup1.text)
        documents_text = re.search('<document>.*</document>', sgml.replace('\n', '')).group(0)
        soup2 = BeautifulSoup(documents_text)
        get_text = lambda e: e.contents[0].strip()
        get_type = lambda d: get_text(d.type)
        get_filename = lambda d: get_text(d.type.sequence.filename)
        documents = soup2.findAll('document')
        data = [
            {'Type': get_type(d), 'Document': get_filename(d)}
            for d in documents
        ]
        return data
    
    def _load_index(self):
        data = self._get_document_info()
        df = pd.DataFrame(data)
        keep = (
            df.Type.isin(self.TYPES) &
            df.Document.map(lambda s: not s.endswith('.pdf'))
            )
        count = keep.sum()
        assert count == 1, df

        filename = df.Document[keep].values[0]
        self.filing['form_path'] = _join(self.filing['folder'], filename)
        self.filing['type'] = df.Type[keep].values[0]

    def _load_form(self):
        cmd = 'RETR %(form_path)s' % self.filing
        self.filing['html'] = self.retr(cmd)
