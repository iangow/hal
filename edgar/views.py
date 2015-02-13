from django.shortcuts import render
from django.http import HttpResponse
from models import Filing

def def_14a(request, folder):
    filing, created = Filing.objects.get_or_create(folder=folder)
    filing.set_html()
    filing.save()
    return HttpResponse(filing.html)
