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
        result = {'folder': folder}
        
        text = self.retr('LIST %(folder)s' % result)
        df = pd.read_fwf(StringIO(text), header=None)
        filenames = df[8]
        is_index = filenames.map(lambda s: hasattr(s, 'endswith') and s.endswith('index.htm'))
        assert is_index.sum() == 1
        filename = filenames[is_index].values[0]
        result['index_path'] = _join(folder, filename)

        cmd = 'RETR %(index_path)s' % result
        text = self.retr(cmd)
        soup1 = BeautifulSoup(text)
        soup2 = BeautifulSoup(soup1.text)
        get_text = lambda e: e.contents[0].strip()
        get_type = lambda d: get_text(d.type)
        get_filename = lambda d: get_text(d.type.sequence.filename)
        df = pd.DataFrame([
            {'Type': get_type(d), 'Document': get_filename(d)}
            for d in soup2.findAll('document')
        ])
        keep = (
            df.Type.isin(self.TYPES) &
            df.Document.map(lambda s: not s.endswith('.pdf'))
            )
        count = keep.sum()
        assert count == 1, df

        filename = df.Document[keep].values[0]
        result['form_path'] = _join(folder, filename)
        result['type'] = df.Type[keep].values[0]

        cmd = 'RETR %(form_path)s' % result
        result['html'] = self.retr(cmd)
        return result
