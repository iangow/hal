from BeautifulSoup import BeautifulSoup, Tag
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from models import Filing, Highlight, Db
from random import randint
import json
from django.contrib.auth.decorators import login_required
import os


def home(request):
    return HttpResponse('Hello, World!')


def _load(folder):
    f, created = Filing.objects.get_or_create(folder=folder)
    if not f.downloaded():
        f.download()
    return f


def random_filing(request):
    n = Filing.objects.count()
    i = randint(0, n-1)
    f = Filing.objects.all()[i]

    url = reverse('highlight', args=[f.folder])
    absolute_url = request.build_absolute_uri(url)
    # highlight_url = reverse('highlight') + '?url=' + absolute_url
    return redirect(absolute_url)


def _raw_filing(f):
    html_or_text = f.text
    if f.text_file:
        html = '<html><head></head><body><pre>%s</pre></body></html>' % html_or_text
    else:
        html = html_or_text

    try:
        # Trim off doctype that is breaking beautiful soup.
        i = html.lower().index('<html>')
        trimmed = html[i:len(html)]
    except ValueError:
        # Surround content with html tag.
        trimmed = '<html>%s</html>' % html

    return trimmed


@login_required(login_url='/admin/login/')
def highlight(request, folder):
    f = _load(folder)
    filing_html = _raw_filing(f)
    director_names = json.dumps(f.director_names())
    highlight_html = render_to_string('highlight.html', {
        'director_names': director_names,
        'STORE_URL': os.environ['STORE_URL'],
        'user': request.user
    })
    html = _insert(filing_html, highlight_html)
    return HttpResponse(html)


def _insert(doc, html_block):
    tree = BeautifulSoup(doc)
    l = tree.findAll('html')
    assert len(l) == 1, doc[0:400]
    html = l[0]

    block = BeautifulSoup(html_block)
    if html.head is None:
        html.insert(0, Tag(tree, 'head'))
    html.head.insert(0, block)

    return html.prettify()


def companies(request):
    query_string = request.GET['q']
    query = ''.join([
        "SELECT equilar_id, company FROM companies WHERE lower(company) LIKE '%",
        query_string.lower(),
        "%' LIMIT 10;"
    ])
    rows = Db.execute(query)
    my_id = lambda x: ' - '.join([x[1], str(x[0])])
    f = lambda x: {'id': my_id(x), 'text': x[1]}
    dicts = map(f, rows) + [{'text': 'Company Not Found', 'id': -1}]
    return JsonResponse({'items': dicts})


def _raw_directorships(folder):
    filing = Filing.objects.get(folder=folder)
    other_directorships = filing.other_directorships()

    d = {}
    for other in other_directorships:
        k = other.pop('director')
        if k not in d:
            d[k] = {'highlights': [], 'directorships': []}
        d[k]['directorships'].append(other)

    highlights = Highlight.objects.filter(uri__endswith=folder)
    for h in highlights:
        if h.text in d:
            d[h.text]['highlights'].append(h)

    for k in d.keys():
        if len(d[k]['highlights']) == 0:
            del d[k]

    return render_to_string('directorships.html', {'directors': sorted(d.items())})


@login_required(login_url='/admin/login/')
def directorships(request, folder):
    raw_html = _raw_directorships(folder)
    highlight_html = render_to_string('highlight_companies.html', {
        'STORE_URL': os.environ['STORE_URL'],
        'user': request.user
    })
    html = _insert(raw_html, highlight_html)
    return HttpResponse(html)
