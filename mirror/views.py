from BeautifulSoup import BeautifulSoup
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from models import Filing
from random import randint
import requests
import json
from django.contrib.auth.decorators import login_required
import os


@csrf_exempt
def mirror(request, folder):
    f = Filing.objects.get(folder=folder)

    if not f.downloaded():
        f.download()

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
    relative_url = reverse('filing', args=[folder])
    absolute_url = request.build_absolute_uri(relative_url)

    f = Filing.objects.get(folder=folder)
    director_names = json.dumps(f.director_names())

    html_or_text = requests.get(absolute_url).text
    if f.text_file:
        html = '<html><head></head><body><pre>%s</pre></body></html>' % html_or_text
    else:
        html = html_or_text

    tree = BeautifulSoup(html)
    l = tree.findAll('html')
    assert len(l) == 1
    html = l[0]

    text = render(request, 'highlight.html', {
        'director_names': director_names,
        'STORE_URL': os.environ['STORE_URL']
    }).content
    block = BeautifulSoup(text)
    html.head.insert(0, block)

    return HttpResponse(html.prettify())
