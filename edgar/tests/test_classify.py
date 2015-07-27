from edgar import classify
from StringIO import StringIO
import pandas as pd
import glob
from nose.plugins.attrib import attr
from nose.tools import assert_equal


def test_paragraphs():
    md = '''
> This is a short excerpt with a couple paragraphs. We need to make sure
> this wraps over multiple lines.
>
> This is the second paragraph.
'''.strip()

    buffer = StringIO(md)
    df = classify.Corpus._markdown_to_data_frame(buffer)
    assert_equal(df.shape[0], 2)


def test_corpus():
    TEXT = '''
< This is a biography section.
>
> This is not.
'''
    buffer = StringIO(TEXT)

    c = classify.Corpus([buffer], n_bio_words=3, min_bio_word_count=1)

    assert 'bio' in c.lines and 'text' in c.lines
    assert c.lines.shape[0] == 2


def test_optimal_region():
    p = pd.Series([0, 0, .1, .1, .3, 0, 0, .01])
    region = classify.Classifier._optimal_region(p)
    assert region == (2, 4)


@attr('slow')
def test_classifier():
    all_md = glob.glob('corpus/*.md')
    train = classify.Corpus(filepaths_or_buffers=all_md[0:-1])
    test = classify.Corpus(filepaths_or_buffers=[all_md[-1]])

    e = classify.Classifier()
    e.fit(train.X, train.y)
    e.predict(test.X)


def test_bios():
    expected = {
        'Ailey, Alvin': 'Mr. Ailey was born in 1931 in Rogers, Texas.',
        'Barker, Bob': 'Bob Barker is currently 91 years young.',
        'Coolidge, Calvin': 'Calvin Coolidge was born on July 4, 1872!',
    }

    bio_region = '\n'.join(expected.values())
    names = expected.keys()

    actual = classify.Splitter().split(bio_region, names)
    assert actual == expected


def _test_bios(path):
    df = classify.Corpus._markdown_to_data_frame(path)
    bio_region = '\n'.join(df.text[df.bio])
    names = classify.Corpus.director_names(path)
    classify.Splitter().split(bio_region, names)


@attr('slow')
def _test_bios_on_corpus():
    # TODO: Need to fix splitter: corpus/1007330-000095014405003532.md
    all_md = glob.glob('corpus/*.md')
    for path in all_md:
        _test_bios(path)


def test_tag():
    s = classify.Splitter()
    df = pd.DataFrame({
        0: [1, 2, 3, 4, 5],
        1: [5, 4, 3, 2, 1],
        2: [2, 2, 4, 2, 2]
    })

    assert (s._peaks(df) == pd.Series(data=[0, 2, 4], index=[1, 2, 0])).all()
    assert s._cutoffs(df) == [2, 3]
    assert s._tag(df) == [1, 1, 2, 0, 0]
