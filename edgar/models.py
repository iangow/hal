from django.db import models
import requests
import pandas as pd
import re
from BeautifulSoup import BeautifulSoup

def index_url(folder_url):
    '''
    >>> index_url('http://www.sec.gov/Archives/edgar/data/769397/000076939713000018')
    u'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/0000769397-13-000018-index.htm'
    '''
    df = pd.read_html(folder_url, header=0)[0]
    df['is_index'] = df.Name.map(lambda s: hasattr(s, 'endswith') and s.endswith('index.htm'))
    assert df.is_index.sum() == 1
    filename = df.Name[df.is_index].values[0]
    return '/'.join([folder_url, filename])

def def_14a_url(folder_url):
    '''
    >>> def_14a_url('http://www.sec.gov/Archives/edgar/data/769397/000076939713000018')
    u'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/proxydocument.htm'
    '''
    df = pd.read_html(index_url(folder_url), header=0)[0]
    df['def_14a'] = (df.Description == 'DEF 14A') | (df.Type == 'DEF 14A')
    assert df.def_14a.sum() == 1, df
    filename = df.Document[df.def_14a].values[0]
    return '/'.join([folder_url, filename])

class Filing(models.Model):
    folder = models.CharField(max_length=100, unique=True)
    text = models.TextField(default='')
    html = models.TextField(default='')

    def set_text(self, prefix='http://www.sec.gov/Archives/edgar/data/'):
        if not self.text:
            response = requests.get(
                def_14a_url(prefix + self.folder)
            )
            self.text = response.text

    def set_html(self):
        self.set_text()
        tree = BeautifulSoup(self.text)
        l = tree.findAll('html')
        assert len(l) == 1
        html = l[0]

        with open('edgar/annotator.html') as f:
            text = f.read()
        annotator = BeautifulSoup(text)
        html.head.insert(0, annotator)

        self.html = html.prettify()
