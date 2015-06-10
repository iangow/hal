from django.db import models
import requests
import os
from sec_utils import Filing


class Directors(models.Model):
    '''
    This model was created by inspected the director.director table on
    Ian's server. Let's use the admin to make sure that django can
    read data from the server.
    '''
    
    director_id = models.TextField(blank=True)
    company = models.TextField(blank=True)
    director = models.TextField(blank=True)
    ticker = models.TextField(blank=True)
    fy_end = models.DateField(blank=True, null=True)
    gender = models.TextField(blank=True)
    age = models.IntegerField(blank=True, null=True)
    chairman = models.NullBooleanField()
    vice_chairman = models.NullBooleanField()
    lead_independent_director = models.NullBooleanField()
    audit_committee_financial_expert = models.NullBooleanField()
    start_date = models.DateField(blank=True, null=True)
    term_end_date = models.DateField(blank=True, null=True)
    tenure_yrs = models.FloatField(blank=True, null=True)
    num_committees = models.IntegerField(blank=True, null=True)
    committees = models.TextField(blank=True)
    fileyear = models.IntegerField(blank=True, null=True)
    insider_outsider_related = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'director\".\"director'


class File(models.Model):

    REMOTE_ROOT = 'http://www.sec.gov/Archives/edgar/data'
    LOCAL_ROOT = os.environ.get('LOCAL_ROOT', 'edgar-data')

    remote_url = models.CharField(max_length=200, unique=True)

    def path(self):
        return self.remote_url.replace(self.REMOTE_ROOT, '')[1:]

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


def load(folder):
    folder_url = '/'.join([File.REMOTE_ROOT, folder])
    matches = list(File.objects.filter(remote_url__startswith=folder_url))
    count = len(matches)
    assert count in [0, 1]
    if count == 1:
        return matches[0]

    filing = Filing(folder)
    if filing.is_def_14a:
        return File.objects.create(remote_url=filing.def_14a_url)
    else:
        return filing
