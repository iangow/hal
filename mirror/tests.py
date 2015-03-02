from django.test import TestCase
from models import Site, File
import os


class MyTestCase(TestCase):

    def setUp(self):
        self.path = '769397/000076939713000018/0000769397-13-000018.hdr.sgml'

    def test_download(self):
        s = Site.objects.create(
            local_path='edgar-files',
            remote_url='http://www.sec.gov/Archives/edgar/data/'
        )
        f = File.objects.create(
            site=s, path=self.path
        )
        f.download()
        os.remove(f.local_path())
