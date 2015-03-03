from django.core.management.base import BaseCommand
from mirror.models import File
import pandas as pd
import sys


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


class Command(BaseCommand):
    args = '<folder folder ...>'
    help = 'Create entry for corresponding DEF 14A document'

    def handle(self, *args, **options):
        n = len(args)
        for i, folder in enumerate(args):
            f = load(folder)
            path = f.local_path()
            counter = i + 1
            message = '\r[%(counter)d / %(n)d - %(path)s]' % locals()
            sys.stdout.write(message)
            sys.stdout.flush()
