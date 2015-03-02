from django.shortcuts import render
from django.http import HttpResponse
from models import Filing
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def def_14a(request, folder):
    filing, created = Filing.objects.get_or_create(folder=folder)
    filing.save()
    return HttpResponse(filing.text)
