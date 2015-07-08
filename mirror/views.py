from BeautifulSoup import BeautifulSoup, Tag
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from models import Filing, Highlight
from random import randint
import json
from django.contrib.auth.decorators import login_required
import os
from django.db import connection


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


@login_required(login_url='/admin/login/')
def highlight(request, folder):
    f = _load(folder)

    director_names = json.dumps(f.director_names())

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

    return _highlight_page(request, trimmed, director_names)


def _highlight_page(request, raw_html, items):
    tree = BeautifulSoup(raw_html)
    l = tree.findAll('html')
    assert len(l) == 1, raw_html[0:400]
    html = l[0]

    text = render_to_string('highlight.html', {
        'director_names': items,
        'STORE_URL': os.environ['STORE_URL'],
        'user': request.user
    })
    block = BeautifulSoup(text)
    if html.head is None:
        html.insert(0, Tag(tree, 'head'))
    html.head.insert(0, block)

    return HttpResponse(html.prettify())


@login_required(login_url='/admin/login/')
def directorships(request, folder):
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

    return render(request, 'directorships.html', {'directors': sorted(d.items())})
