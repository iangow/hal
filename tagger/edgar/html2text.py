from bs4 import BeautifulSoup, NavigableString, Tag
import textwrap
import re


# https://github.com/aaronsw/html2text/blob/master/html2text.py#L377
# http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/view/head:/bs4/element.py#L1101
PARAGRAPH_TAGS = [
    'blockquote', 'hr', 'table', 'tr', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre',
]


def element_to_text(element):
    l = []

    for child in element:
        if isinstance(child, NavigableString) and not _is_comment(child):
            # A NavigableString is also a unicode object.
            clean_text = _replace_whitespace_with_one_space(child)
            l.append(clean_text)
        elif isinstance(child, Tag):
            l.append(element_to_text(child))

    if element.name in PARAGRAPH_TAGS:
        # Put two line breaks around paragraphs.
        l = ['\n\n'] + l + ['\n\n']

    return ''.join(l)


def _is_comment(element):
    return isinstance(element, NavigableString) and element.PREFIX != ''


def clean(html):
    soup = BeautifulSoup(html, 'html5lib')
    _row_handler(soup)
    text = element_to_text(soup).encode('utf-8')
    pars = paragraphs(text)
    wrapped = map(textwrap.fill, pars)
    text = '\n\n'.join(wrapped)
    return _handle_multibyte_characters(text)


# def clean(html):
#     soup = BeautifulSoup(html, 'html5lib')

#     # These two lines are important for dealing with malformed html.
#     pretty = soup.prettify()
#     soup = BeautifulSoup(pretty, 'html5lib')

#     _row_handler(soup)
#     strings = soup._all_strings()
#     wrapped = map(_clean_element, strings)
#     text = '\n\n'.join(wrapped)
#     text = '\n\n'.join(paragraphs(text)).strip()
#     return _handle_multibyte_characters(text)


def _row_handler(soup):
    for row in soup.findAll('tr'):
        text = row.get_text(separator='; ', strip=True)
        row.contents = [NavigableString(text)]


def _handle_multibyte_characters(s):
    assert type(s) == str
    nbsp_removed = s.replace('\xc2\xa0', ' ')
    return nbsp_removed


def _replace_whitespace_with_one_space(s):
    return re.sub('\s+', ' ', s)


def paragraphs(text):
    assert type(text) == str
    return re.split('\n\s+', text.strip())
