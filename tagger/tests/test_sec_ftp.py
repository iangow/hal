from ..sec_ftp import Client, _parse
from nose.plugins.attrib import attr
import re


@attr('slow')
def test_client():
    c = Client()
    c.login()

    d = c.load('769397/000076939713000018')
    assert d['index_path'] == '769397/000076939713000018/0000769397-13-000018-index.htm'
    assert d['form_path'] == u'769397/000076939713000018/proxydocument.htm'

    assert c.load('1084869/000108486908000022')['form_path'] == u'1084869/000108486908000022/proxy.txt'
    assert c.load('1364742/000134100410000059')['type'] == u'DEF 14C'
    assert c.load('1001871/000115752306006856')['form_path'] == u'1001871/000115752306006856/a5187774.txt'
    assert c.load('1100663/000119312509185679')['form_path'] == u'1100663/000119312509185679/ddef14a.htm'
    assert c.load('310354/000031035412000032')['form_path'] == u'310354/000031035412000032/proxy.htm'

    c.logout()


def test_parse():
    sgml = '''
<DOCUMENT>
<TYPE>DEF 14A
<SEQUENCE>1
<FILENAME>ddef14a.htm
<DESCRIPTION>DEFINITIVE PROXY STATEMENT
<TEXT>
Hello, World
</TEXT>
</DOCUMENT>
'''
    d = _parse(sgml)
    assert not d['text_file']

    sgml = '''
<DOCUMENT>
<TYPE>DEF 14A
<SEQUENCE>1
<FILENAME>c90407ddef14a.txt
<DESCRIPTION>DEFINITIVE PROXY STATEMENT
<TEXT>
Hello, World
</TEXT>
</DOCUMENT>
'''
    d = _parse(sgml)
    assert d['text_file']

    sgml = '''<DOCUMENT>
<TYPE>DEF 14A
<SEQUENCE>1
<FILENAME>proxy.txt
<TEXT>
No description!
</TEXT>
</DOCUMENT>'''

    d = _parse(sgml)
