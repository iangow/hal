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
from django.shortcuts import render


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


def _raw_directorships(folder, director_id):
    filing = Filing.objects.get(folder=folder)
    other_directorships = filing.other_directorships()

    directorships = [d for d in other_directorships if d['director_id'] == director_id]
    names = list(set([d['director'] for d in directorships]))

    qs = Highlight.objects.filter(uri__endswith=folder).order_by('created')
    highlights = [h for h in qs if h.text in names]

    return render_to_string('directorships.html', locals())


@login_required(login_url='/admin/login/')
def directorships(request, folder, director_id):
    raw_html = _raw_directorships(folder, director_id)
    highlight_html = render_to_string('highlight_companies.html', {
        'STORE_URL': os.environ['STORE_URL'],
        'user': request.user
    })
    html = _insert(raw_html, highlight_html)
    return HttpResponse(html)


def biographies_to_highlight(request):
    rows = Db._exec('biographies_to_highlight.sql')
    dicts = map(lambda x: dict(zip(['folder', 'director_id', 'director'], x)), rows)
    return render(request, 'biographies_to_highlight.html', locals())
