from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import re
from itertools import groupby


def _bio_segment(doc):
    x = doc['_source']
    l = x.get('uri').split('/')
    filing = '/'.join(l[-2:len(l)])

    return {
        'filing': filing,
        'director_name': x.get('text'),
        'text': x.get('quote'),
        'username': x.get('username', '')
    }


def bio_segments():
    es = Elasticsearch()
    # Sort highlights by filing, director, time created
    for doc in scan(es, query={}, sort=['uri', 'text', 'created'], index='annotator'):
        yield _bio_segment(doc)


def bios():
    filing_and_director = lambda d: d['filing'] + d['director_name']
    for k, g in groupby(bio_segments(), filing_and_director):
        l = list(g)
        result = {
            'filing': l[0]['filing'],
            'director_name': l[0]['director_name'],
            'text': '\n\n'.join([s['text'] for s in l])
        }
        yield result


def clean(text):
    lines = text.split('\n')
    keep = [l for l in lines if re.search('[a-zA-Z0-9]', l) is not None]
    return '\n'.join(keep)


if __name__ == '__main__':
    for d in bios():
        print '\n# %(filing)s - %(director_name)s\n' % d
        print clean(d['text']).encode('utf-8')
