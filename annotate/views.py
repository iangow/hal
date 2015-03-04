from mirror.models import File
from random import randint
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect


def random(request):
    n = File.objects.count()
    i = randint(0, n-1)
    f = File.objects.all()[i]
    path = f.path()
    url = reverse('mirror.views.mirror', args=[path])
    absolute_url = request.build_absolute_uri(url)
    highlight_url = reverse('highlight') + '?url=' + absolute_url
    return redirect(highlight_url)
