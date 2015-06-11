from BeautifulSoup import BeautifulSoup
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from models import Filing
from random import randint
import requests
import json


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


def _modify_html(request, url, director_names):
    response = requests.get(url)

    tree = BeautifulSoup(response.text)
    l = tree.findAll('html')
    assert len(l) == 1
    html = l[0]

    text = render(request, 'highlight.html', {'director_names': director_names}).content
    block = BeautifulSoup(text)
    html.head.insert(0, block)

    return html.prettify()


def highlight(request, folder):
    url = reverse('filing', args=[folder])
    absolute_url = request.build_absolute_uri(url)
    f = Filing.objects.get(folder=folder)
    names = json.dumps(f.director_names())
    html = _modify_html(request, absolute_url, director_names=names)
    return HttpResponse(html)
