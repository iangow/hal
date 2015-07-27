'''
A module designed to identify bio regions (and biographies) in DEF 14A
filings.
'''

from collections import defaultdict
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import BaggingClassifier
import glob
import pandas as pd
import re
import json
from fuzzywuzzy import fuzz
import numpy as np
from math import log


class Corpus(object):

    PATHS = glob.glob('corpus/*.md')
    REGEXPS = {
        'education': '(college|university|school|bachelor)',
        'founding': '(co-)?found(ed|er|ing)?',
        'verb': '(retired|spent|gained|brings)',
        'pronoun': r'\b(he|she)\b',
        'position': '(chairman|chief|executive|officer|president)',
    }

    def __init__(self, filepaths_or_buffers=None, **kwargs):
        self.lines = self._read(filepaths_or_buffers)
        self._set_features()

    def _read(self, filepaths_or_buffers=None):
        if filepaths_or_buffers is None:
            filepaths_or_buffers = self.PATHS
        assert type(filepaths_or_buffers) == list
        blocks = []
        for fb in filepaths_or_buffers:
            df = self._markdown_to_data_frame(fb)
            if isinstance(fb, basestring):
                df['path'] = fb
                self._set_director_columns(data=df, path=fb)
            blocks.append(df)
        return pd.concat(blocks, ignore_index=True)

    @classmethod
    def _markdown_to_data_frame(cls, filepath_or_buffer):
        lines = pd.read_fwf(
            filepath_or_buffer,
            [(0, 2), (2, -1)],
            header=None,
            names=['flag', 'text']
        )
        lines['text'] = lines.text.fillna('').astype(str)
        lines['no_words'] = lines.text.map(lambda s: re.search('[a-zA-Z]', s) is None)
        lines['paragraph'] = lines.no_words.cumsum()
        no_blanks = lines[-lines.no_words]
        
        def consolidate(block):
            flags = list(set(block.flag))
            if len(flags) > 1:
                if '>' in flags:
                    flags.remove('>')
            assert len(flags) == 1, block
            return pd.Series({
                'text': ' '.join(block.text),
                'flag': flags[0]
            })

        paragraphs = no_blanks.groupby('paragraph').apply(consolidate)
        paragraphs['bio'] = paragraphs.flag != '>'
        paragraphs['words'] = paragraphs.text.map(lambda s: re.findall("[-'a-zA-Z]+", s))
        paragraphs['line'] = range(paragraphs.shape[0])
        return paragraphs

    @classmethod
    def get_bio_words(cls, df, n_bio_words=25, min_bio_word_count=25):
        def init():
            return [0, 0]
        d = defaultdict(init)
        for i, row in df.iterrows():
            for word in row['words']:
                d[word][0] += 1
                if row['bio']:
                    d[word][1] += 1

        word_counts = pd.DataFrame([
            {'word': word, 'total': l[0], 'bio': l[1]} for word, l in d.items()
        ])
        word_counts['non_bio'] = word_counts['total'] - word_counts['bio']
        word_counts = word_counts[word_counts['total'] >= min_bio_word_count]
        word_counts['ratio'] = word_counts.bio / word_counts.non_bio

        return list(word_counts.sort('ratio', ascending=False).head(n_bio_words)['word'])

    @property
    def X(self):
        df = self.lines
        select = [c for c in df.columns if c.startswith('_')]
        return df[select]

    @property
    def y(self):
        return self.lines.bio

    @classmethod
    def director_names(cls, path):
        # TODO: This won't work with database.
        with open('corpus/directors.json') as f:
            d = json.load(f)
        folder = re.sub('[^-0-9]', '', path).replace('-', '/')
        return map(str, d[folder])

    def _set_director_columns(self, data, path):
        names = self.director_names(path)
        last_names = map(lambda s: s.split(',')[0], names)
        unique_last_names = list(set(last_names))
        for i, last_name in enumerate(unique_last_names):
            contains = lambda s: last_name.lower() in map(lambda t: t.lower(), s)
            data[i] = data.words.map(contains)
        cols = range(len(unique_last_names))
        data['ndirectors'] = data[cols].sum(axis=1)

        data['_one_director'] = data.ndirectors == 1
        # data['_more_than_one_director'] = data.ndirectors > 1

        del data['ndirectors']
        for i in cols:
            del data[i]

    def _set_features(self):
        for name, pattern in self.REGEXPS.items():
            col = '_' + name
            matches = lambda s: log(1 + len(re.findall(pattern, s, re.IGNORECASE)))
            self.lines[col] = self.lines.text.map(matches)

            if '_one_director' in self.lines:
                interaction = '_one_director_x' + col
                self.lines[interaction] = self.lines._one_director * self.lines[col]


class MyEstimator(BaggingClassifier):

    def __init__(self):
        super(MyEstimator, self).__init__(
            base_estimator=LogisticRegression(),
            n_estimators=10,
            max_samples=1.0,
            max_features=0.5,
            bootstrap=False,
            bootstrap_features=False
        )

    def p_hat(self, X):
        assert True in self.classes_
        i = list(self.classes_).index(True)
        P = self.predict_proba(X)
        return P[:, i]


class Classifier(object):

    def __init__(self):
        self.estimator = MyEstimator()

    def fit(self, X, y):
        self.estimator.fit(X, y)

    def predict(self, X, lines=None):
        p_hat = pd.Series(self.estimator.p_hat(X))
        region = self._optimal_region(p_hat)
        y_hat = pd.Series([0 for i in range(len(p_hat))])
        y_hat[region[0]:region[1]] = 1
        if lines is not None:
            bio_region = '\n'.join(lines.text[region[0]:region[1]])
        return locals()

    @classmethod
    def _optimal_region(cls, p, penalty=0.05, lookahead=1000):
        def f(i, j):
            assert i <= j
            region = range(i, j+1)
            width = (j - i + 1)
            return p[region].sum() - penalty * width

        maxval = 0
        argmax = (0, 0)
        for i in p.index[p > penalty]:
            for j in p.index[(p > penalty) & (p.index >= i) & (p.index <= i + lookahead)]:
                val = f(i, j)
                if val > maxval:
                    maxval = val
                    argmax = (i, j)

        return argmax


class Splitter(object):

    def split(self, text, names):
        self.text = text
        self.names = names
        self._set_lines()
        return self._bios()

    @classmethod
    def _my_distance(cls, name):
        assert type(name) == str
        names = name.split(', ')
        assert len(names) == 2
        last_name, first_name = names

        def result(line):
            assert type(line) == str
            primary_distance = fuzz.partial_ratio(last_name, line)
            secondary_distance = fuzz.partial_ratio(first_name, line)
            return primary_distance + (secondary_distance / 1000.0)

        return result

    def _set_lines(self):
        lines = pd.DataFrame({
            'text': self.text.splitlines()
        })

        for i, name in enumerate(self.names):
            lines[i] = lines.text.map(self._my_distance(name))

        self.lines = lines

    def _peaks(self, distances):
        df = distances.copy()
        df['max'] = df.apply(lambda d: np.max(d), axis=1)
        df['argmax'] = df.apply(lambda d: np.argmax(d), axis=1)
        df.sort('max', inplace=True, ascending=False)
        d = {}
        for i, row in df.iterrows():
            if row['argmax'] not in d:
                d[row['argmax']] = i
        s = pd.Series(d)
        s.sort()
        return s

    def _cutoffs(self, distances):
        peaks = self._peaks(distances)

        cutoffs = []
        for i in range(len(peaks) - 1):
            start = peaks.values[i]
            a = peaks.index[i]
            stop = peaks.values[i + 1]
            b = peaks.index[i + 1]
            for k in range(start, stop + 1):
                if distances[b][k] > distances[a][k]:
                    cutoffs.append(k)
                    break

        assert len(cutoffs) == len(peaks) - 1, cutoffs
        return cutoffs

    def _tag(self, distances):
        peaks = self._peaks(distances)
        cutoffs = self._cutoffs(distances)

        tag = []
        for i in range(len(peaks)):
            start = 0 if i == 0 else cutoffs[i - 1]
            stop = cutoffs[i] if i < (len(peaks) - 1) else distances.shape[0]
            col = peaks.index[i]
            for k in range(start, stop):
                tag.append(col)
        return tag

    def _bios(self):
        distances = self.lines[range(len(self.names))]
        columns = self._tag(distances)
        self.lines['tag'] = map(lambda i: self.names[int(i)], columns)
        gb = self.lines.groupby('tag')
        pairs = [(name, '\n'.join(block.text)) for name, block in gb]
        result = dict(pairs)
        if len(result.keys()) < len(self.names):
            missing = [n for n in self.names if n not in result]
            assert False, 'Missing names: ' + json.dumps(missing)
        return result
