from django.shortcuts import render
from django.http import HttpResponse
from BeautifulSoup import BeautifulSoup
import requests

def _modify_html(url):
    response = requests.get(url)
    
    tree = BeautifulSoup(response.text)
    l = tree.findAll('html')
    assert len(l) == 1
    html = l[0]

    with open('highlighter/highlight.html') as f:
        text = f.read()
    block = BeautifulSoup(text)
    html.head.insert(0, block)

    return html.prettify()

def highlight(request):
    url = request.GET['url']
    html = _modify_html(url)
    return HttpResponse(html)
