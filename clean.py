'''
Let's write some code to pull out director bios from raw HTML.
'''

from random_filing import *
from fuzzywuzzy import fuzz
import glob
import json

engine, session = get_engine_and_session(db='db.sqlite')

def compare(folder):
    f = get_filing(session, folder)
    actual = clean(f.html)

    path = target_path(folder)
    with open(path) as f:
        target = f.read()

    d = {
        'ratio': fuzz.ratio(actual, target),
        'partial_ratio': fuzz.partial_ratio(actual, target),
        'folder': folder,
    }
    print json.dumps(d, indent=2)

path2folder = lambda s: re.sub('[^-0-9]', '', s).replace('-', '/')

def compare_all():
    targets = glob.glob('./targets/*.md')
    for path in targets:
        compare(path2folder(path))
        break

compare_all()
