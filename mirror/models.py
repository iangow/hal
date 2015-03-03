from django.db import models
import requests
import os
import pandas as pd


class File(models.Model):

    REMOTE_ROOT = 'http://www.sec.gov/Archives/edgar/data'
    LOCAL_ROOT = os.environ.get('LOCAL_ROOT', 'edgar-data')

    remote_url = models.CharField(max_length=200, unique=True)

    def local_path(self):
        assert self.remote_url.startswith(self.REMOTE_ROOT)
        return self.remote_url.replace(self.REMOTE_ROOT, self.LOCAL_ROOT)

    def downloaded(self):
        return os.path.exists(self.local_path())

    def download(self):
        path = self.local_path()
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        response = requests.get(self.remote_url)
        with open(path, 'w') as f:
            f.write(response.text)
        assert self.downloaded()

    def read(self):
        with open(self.local_path()) as f:
            return f.read()


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


def load(folder):
    folder_url = '/'.join([File.REMOTE_ROOT, folder])
    matches = list(File.objects.filter(remote_url__startswith=folder_url))
    count = len(matches)
    assert count in [0, 1]
    if count == 1:
        return matches[0]
    else:
        doc_url = def_14a_url(folder_url)
        f = File.objects.create(remote_url=doc_url)
        return f
