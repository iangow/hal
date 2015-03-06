import pandas as pd

def _join(*args):
    return '/'.join(args)

def index_url(url):
    '''
    >>> index_url('http://www.sec.gov/Archives/edgar/data/769397/000076939713000018')
    u'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/0000769397-13-000018-index.htm'
    '''
    df = pd.read_html(url, header=0)[0]
    df['is_index'] = df.Name.map(lambda s: hasattr(s, 'endswith') and s.endswith('index.htm'))
    assert df.is_index.sum() == 1
    filename = df.Name[df.is_index].values[0]
    return _join(url, filename)

def files(url):
    '''
    >>> files('http://www.sec.gov/Archives/edgar/data/769397/000076939713000018').shape
    (23, 5)
    '''
    return pd.read_html(index_url(url), header=0)[0]

def def_14a_url(url):
    '''
    >>> def_14a_url('http://www.sec.gov/Archives/edgar/data/769397/000076939713000018')
    u'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/proxydocument.htm'

    >>> def_14a_url('http://www.sec.gov/Archives/edgar/data/1084869/000108486908000022')
    u'http://www.sec.gov/Archives/edgar/data/1084869/000108486908000022/proxy.txt'

    >>> def_14a_url('http://www.sec.gov/Archives/edgar/data/1364742/000134100410000059') is None
    True
    '''
    df = files(url)
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
