from django.db import models
import requests
import os


class File(models.Model):

    REMOTE_ROOT = 'http://www.sec.gov/Archives/edgar/data'
    LOCAL_ROOT = os.environ.get('LOCAL_ROOT', 'edgar-data')

    remote_url = models.CharField(max_length=200, unique=True)

    def local_path(self):
        assert self.remote_url.startswith(self.REMOTE_ROOT)
        return self.remote_url.replace(self.REMOTE_ROOT, self.LOCAL_ROOT)

    def downloaded(self):
        return os.path.exists(self.local_path())

    def download(self):
        path = self.local_path()
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        response = requests.get(self.remote_url)
        with open(path, 'w') as f:
            f.write(response.text)
        assert self.downloaded()

    def read(self):
        with open(self.local_path()) as f:
            return f.read()
