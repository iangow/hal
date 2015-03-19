'''
    python benchmark.py

Quickly benchmark how well the code is extracting director bios from
the raw HTML based on the targets contained in the `targets` folder.
'''

from fuzzywuzzy import fuzz
from models import Filing
from multiprocessing import Pool
import codecs
import glob
import os
import pandas as pd
import re

target_md = lambda s: re.sub(Filing.HTTP_ROOT, '', s).replace('/', '-') + '.md'
target_path = lambda s: os.path.join('targets', target_md(s))
path2folder = lambda s: re.sub('[^-0-9]', '', s).replace('-', '/')

def benchmark(folder):
    path = target_path(folder)
    with codecs.open(path, encoding='utf-8') as f:
        target = f.read()

    f = Filing.get(folder)
    actual = f.director_bios()

    d = {
        'ratio': fuzz.ratio(actual, target),
        'folder': folder,
    }
    return d

def benchmark_all():
    paths = glob.glob('targets/*.md')
    folders = map(path2folder, paths)
    pool = Pool(len(folders))
    l = pool.map(benchmark, folders)
    df = pd.DataFrame(l)
    print df.sort('ratio')

if __name__ == '__main__':
    benchmark_all()
