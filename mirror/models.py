from django.db import models
import requests
import os


class Site(models.Model):
    remote_url = models.CharField(max_length=100, unique=True)
    local_path = models.CharField(max_length=100, unique=True)


class File(models.Model):
    site = models.ForeignKey(Site)
    path = models.CharField(max_length=100)

    def remote_url(self):
        return self.site.remote_url + self.path

    def local_path(self):
        return os.path.join(self.site.local_path, self.path)

    def download(self):
        path = self.local_path()
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(path):
            response = requests.get(self.remote_url())
            with open(path, 'w') as f:
                f.write(response.text)
