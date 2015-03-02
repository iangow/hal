from django.test import TestCase
from models import File
import os


class MyTestCase(TestCase):

    def setUp(self):
        self.url = 'http://www.sec.gov/Archives/edgar/data/769397/000076939713000018/0000769397-13-000018.hdr.sgml'

    def test_download(self):
        f = File.objects.create(
            remote_url=self.url
        )
        f.download()
        assert os.path.exists(f.local_path())
        os.remove(f.local_path())
