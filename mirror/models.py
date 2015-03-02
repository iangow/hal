from django.db import models
import requests
import os


class File(models.Model):

    MIRRORS = {
        'http://www.sec.gov/Archives/edgar/data': 'edgar-data'
    }

    remote_url = models.CharField(max_length=200, unique=True)

    def local_path(self):
        for k, v in self.MIRRORS.items():
            if self.remote_url.startswith(k):
                return self.remote_url.replace(k, v)
        raise Exception('Unexpected url', self.remote_url)

    def download(self):
        path = self.local_path()
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(path):
            response = requests.get(self.remote_url)
            with open(path, 'w') as f:
                f.write(response.text)
