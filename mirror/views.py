from django.shortcuts import render
from django.http import HttpResponse
from models import File
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def mirror(request, path):
    url = '/'.join([File.REMOTE_ROOT, path])
    f, created = File.objects.get_or_create(remote_url=url)
    if not f.downloaded():
        f.download()
    return HttpResponse(f.read())
