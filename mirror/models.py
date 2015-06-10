from django.db import models
from sec_ftp import Client


class Directors(models.Model):
    '''
    This model was created by inspected the director.director table on
    Ian's server. Let's use the admin to make sure that django can
    read data from the server.
    '''

    director_id = models.TextField(blank=True, primary_key=True)
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


class Filing(models.Model):

    REMOTE_ROOT = 'http://www.sec.gov/Archives/edgar/data'
    folder = models.CharField(max_length=29, primary_key=True, unique=True)

    KEYS = ['text', 'type', 'text_file']
    text = models.TextField(blank=True, default='')
    type = models.CharField(max_length=7, default='')
    text_file = models.NullBooleanField(default=None)

    # To merge this table of filings with the director information
    # from Equilar, I will have to use the director.equilar_proxies
    # table. With equilar_id and fy_end as merge keys.

    def sec_url(self):
        return '/'.join([self.REMOTE_ROOT, self.folder])

    def downloaded(self):
        return self.text != ''

    def download(self):
        c = Client()
        c.login()
        d = c.load(self.folder)
        c.logout()

        for k in self.KEYS:
            v = d[k]
            setattr(self, k, v)

        assert self.downloaded()
        self.save()
