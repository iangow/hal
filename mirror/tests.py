from django.test import TestCase
from models import Filing
import os
from django.test import Client
from django.core.urlresolvers import reverse
import views


class MyTestCase(TestCase):

    def setUp(self):
        self.folder = '769397/000076939713000018'
        self.f = Filing.objects.create(folder=self.folder)

    def test_download(self):
        self.f.download()

    def test_mirror(self):
        c = Client()
        path = self.folder
        url = reverse(views.mirror, args=[path])
        response = c.get(url)
        self.assertEquals(response.status_code, 200)
