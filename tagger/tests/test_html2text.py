from ..html2text import clean, paragraphs
from nose.tools import assert_equal
import codecs
import re
from nose.plugins.attrib import attr


with codecs.open('tagger/tests/def14a.html', encoding='latin-1') as f:
    EXAMPLE_DEF14A = f.read()


def test_clean():
    actual = clean('<b>heading</b>').strip()
    assert_equal(actual, 'heading')


def test_div_tag():
    html = '<div style="TEXT-INDENT: 0pt;" align="center">UNITED STATES</div>'
    md = 'UNITED STATES'
    assert_equal(clean(html), md)


def test_table_tag():
    html = '<table><tr><td>1</td><td>2</td></tr><tr><td>3</td><td>4</td></tr></table>'
    md = '\n\n'.join(['1; 2', '3; 4'])
    assert_equal(clean(html), md)


def test_non_breaking_space():
    html = 'one&#160;two'
    assert_equal(clean(html), 'one two')


def test_long_line():
    html = '<table><tr><td>Per unit price or other underlying value of transaction computed pursuant to Exchange Act Rule 0-11 (Set forth the amount on which the filing fee is calculated and state how it was determined)</td></tr></table>'
    md = clean(html)
    lines = md.split('\n')
    for line in lines:
        assert len(line) < 80


def test_soup_get_text():
    assert_equal(type(EXAMPLE_DEF14A), unicode)
    md = clean(EXAMPLE_DEF14A)
    md = re.sub('\s+', ' ', md).strip()
    last_sentence = 'EVENT # CLIENT # OFFICE #'
    start = -len(last_sentence)
    assert_equal(md[start:len(md)], last_sentence)


def test_ugly_table():
    with open('tests/ugly_table.html') as f:
        ugly_table = f.read()
    md = clean(ugly_table)
    pars = paragraphs(md)
    assert_equal(len(pars), 7)


def test_long_text():
    html = '''
<p>This is one

sentence.</p>
'''
    md = clean(html)
    assert_equal(md, 'This is one sentence.')


def test_break():
    html = '<p>This is a sentence with <b>emphasis</b>.</p>'
    md = clean(html)
    expected = 'This is a sentence with emphasis.'
    assert_equal(md, expected)
