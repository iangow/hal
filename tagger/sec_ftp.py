'''
A client for downloading filings from the SEC using FTP.
'''

from bs4 import BeautifulSoup
import pandas as pd
from StringIO import StringIO
from io import BytesIO
from ftplib import FTP
import re


def _join(*args):
    return '/'.join(args)


def _parse(sgml):
    regexp = '\n'.join([
        r'^\s*'
        r'<DOCUMENT>',
        r'<TYPE>(?P<type>[^\n]+)',
        r'<SEQUENCE>(?P<sequence>[^\n]+)',
        r'<FILENAME>(?P<filename>[^\n]+)(\n<DESCRIPTION>(?P<description>[^\n]+))?',
        r'<TEXT>',
        r'(?P<text>.*)',
        r'</TEXT>',
        r'</DOCUMENT>'
        r'\s*$'
    ])
    m = re.search(regexp, sgml, re.DOTALL)
    assert m is not None, _head_and_tail(sgml)
    result = m.groupdict()
    result['text_file'] = result['filename'].endswith('.txt')
    return result


def _head_and_tail(text):
    lines = text.split('\n')
    head = lines[0:10]
    tail = lines[-5:-1]
    return '\n'.join(head + tail)


class Client(object):

    TYPES = ['DEF 14A', 'DEF 14C', 'PRE 14A']

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
        df = pd.read_csv(StringIO(text), sep=' +', header=None, engine='python')
        assert df.shape[1] == 9, 'File name has spaces, need to collapse columns.'
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
        sgml = self.retr(cmd)
        d = _parse(sgml)
        for k, v in d.items():
            if k in self.filing:
                assert v == self.filing[k], k
            self.filing[k] = v
