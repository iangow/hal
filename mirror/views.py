from django.http import HttpResponse
from models import Filing
from django.views.decorators.csrf import csrf_exempt
from random import randint
from django.core.urlresolvers import reverse
from django.shortcuts import redirect


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

    url = reverse('mirror.views.mirror', args=[f.folder])
    absolute_url = request.build_absolute_uri(url)
    # highlight_url = reverse('highlight') + '?url=' + absolute_url
    return redirect(absolute_url)
