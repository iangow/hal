import pandas as pd


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


def _doc(folder_url):
    '''
    Returns the html document submitted to edgar. Ignores images and
    the complete submission file.

    >>> _doc('http://www.sec.gov/Archives/edgar/data/769397/000076939713000018')
    {u'Document': u'proxydocument.htm', u'Type': u'DEF 14A', u'Description': u'DEF 14A', u'Seq': 1.0, u'Size': 2205821}

    >>> _doc('http://www.sec.gov/Archives/edgar/data/54991/000095015202009613')
    {u'Document': u'l97695bdef14a.htm', u'Type': u'DEF 14A', u'Description': u'KEITHLEY INSTRUMENTS DEFINITIVE PROXY', u'Seq': 1.0, u'Size': 187133}
    '''
    exclude = {
        'Type': ['GRAPHIC', ],
        'Description': ['Complete submission text file', ]
    }
    df = pd.read_html(index_url(folder_url), header=0)[0]
    for k, l in exclude.items():
        for v in l:
            drop = df[k] == v
            df = df[-drop]

    # Drop pdf files
    pdf_file = df.Document.map(lambda s: s.endswith('.pdf'))
    df = df[-pdf_file]

    assert df.shape[0] == 1, df
    return df.ix[0].to_dict()


def def_14a_url(folder_url):
    '''
    >>> def_14a_url('http://www.sec.gov/Archives/edgar/data/769397/000076939713000018')
    u'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/proxydocument.htm'
    '''
    d = _doc(folder_url)
    if not d['Type']:
        d['Type'] = d['Description']

    if d['Type'] == 'DEF 14A':
        return '/'.join([folder_url, d['Document']])
    else:
        print d
