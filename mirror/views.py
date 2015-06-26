from BeautifulSoup import BeautifulSoup, Tag
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from models import Filing
from random import randint
import json
from django.contrib.auth.decorators import login_required
import os
from django.db import connection, OperationalError


def home(request):
    return HttpResponse('Hello, World!')


def _load(folder):
    try:
        f = Filing.objects.get(folder=folder)
    except Filing.DoesNotExist:
        f = Filing(folder=folder)
    if not f.downloaded():
        f.download()
    return f


def mirror(request, folder):
    f = _load(folder)
    if f.text_file:
        return HttpResponse(f.text, content_type='text/plain')
    return HttpResponse(f.text)


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

    tree = BeautifulSoup(trimmed)
    l = tree.findAll('html')
    assert len(l) == 1, html[0:400]
    html = l[0]

    text = render(request, 'highlight.html', {
        'director_names': director_names,
        'STORE_URL': os.environ['STORE_URL']
    }).content
    block = BeautifulSoup(text)
    if html.head is None:
        html.insert(0, Tag(tree, 'head'))
    html.head.insert(0, block)

    return HttpResponse(html.prettify())


def companies(request):
    query_string = request.GET['q']
    query = ''.join([
        "SELECT equilar_id, company FROM director.company_names WHERE lower(company) LIKE '%",
        query_string.lower(),
        "%' LIMIT 10;"
    ])
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    my_id = lambda x: ' - '.join([x[1], str(x[0])])
    f = lambda x: {'id': my_id(x), 'text': x[1]}
    dicts = map(f, rows)
    return JsonResponse({'items': dicts})


def disclosures(request):
    return render(request, 'disclosures.html')
