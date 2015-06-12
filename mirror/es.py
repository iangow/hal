from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json
import re


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


def bios():
    es = Elasticsearch()
    last = {}
    for doc in scan(es, query={}, sort=['uri', 'text', 'created'], index='annotator'):
        seg = _bio_segment(doc)
        yield seg


def clean(text):
    lines = text.split('\n')
    keep = [l for l in lines if re.search('[a-zA-Z0-9]', l) is not None]
    return '\n'.join(keep)


if __name__ == '__main__':
    for d in bios():
        print '\n# %(username)s - %(filing)s - %(director_name)s\n' % d
        print clean(d['text']).encode('utf-8')
