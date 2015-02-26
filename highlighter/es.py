from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import json

def _dict(doc, keys=['quote', 'text', 'uri', 'ranges']):
    return dict(
        [(k, doc['_source'].get(k)) for k in keys]
    )

def documents(index='annotator'):
    es = Elasticsearch()
    for doc in scan(es, query={}, index=index):
        yield _dict(doc)

if __name__ == '__main__':
    for d in documents():
        print json.dumps(d, indent=2)
