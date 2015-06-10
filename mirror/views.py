from django.http import HttpResponse
from models import Filing
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


@csrf_exempt
def mirror(request, folder):
    f = Filing.objects.get(folder=folder)

    if not f.downloaded():
        f.download()

    if f.text_file:
        return HttpResponse(f.text, content_type='text/plain')
    return HttpResponse(f.text)
