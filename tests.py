from django.test import TestCase
from models import File
import os
from django.test import Client
from django.core.urlresolvers import reverse
import views


class MyTestCase(TestCase):

    def setUp(self):
        self.url = 'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/0000769397-13-000018.hdr.sgml'
        self.f = File.objects.create(remote_url=self.url)

    def test_download(self):
        self.f.download()
        os.remove(self.f.local_path())

    def test_mirror(self):
        c = Client()
        path = self.f.remote_url.replace(File.REMOTE_ROOT, '')
        url = reverse(views.mirror, args=[path])
        response = c.get(url)
        self.assertEquals(response.status_code, 200)
        os.remove(self.f.local_path())
