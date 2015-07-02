from django.db import models
from sec_ftp import Client
from django.db import connection, OperationalError
from jsonfield import JSONField
from django.contrib.auth.models import User


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
    text = models.TextField(blank=True, null=True, default=None)
    type = models.CharField(max_length=7, blank=True, null=True, default=None)
    text_file = models.NullBooleanField(blank=True, default=None)

    # To merge this table of filings with the director information
    # from Equilar, I will have to use the director.equilar_proxies
    # table. With equilar_id and fy_end as merge keys.

    def sec_url(self):
        return '/'.join([self.REMOTE_ROOT, self.folder])

    def downloaded(self):
        return self.text is not None and len(self.text) > 0

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

    @classmethod
    def sync(cls):
        old_count = cls.objects.count()

        with open('mirror/load_filings.sql') as f:
            sql = f.read()
        cursor = connection.cursor()
        cursor.execute(sql)

        new_count = cls.objects.count()
        return new_count - old_count

    def _file_name(self):
        l = self.folder.split('/')
        assert len(l) == 2
        cik, accession = l
        assert len(accession) == 18
        return 'edgar/data/%s/%s-%s-%s.txt' % (
            cik, accession[0:10], accession[10:12], accession[12:18]
        )

    def director_names(self):
        with open('mirror/director_names.sql') as f:
            template = f.read()
            sql = template % self._file_name()
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
        except OperationalError:
            cursor.execute("SELECT 'none';")
        rows = cursor.fetchall()
        names = [r[0] for r in rows]
        return sorted(list(set(names)))


class Biography(models.Model):

    filing = models.ForeignKey(Filing)
    director_name = models.TextField()
    text = models.TextField()

    class Meta:
        unique_together = ('filing', 'director_name')


class File:
    pass


class BiographySegment(models.Model):
    id = models.TextField(primary_key=True, unique=True)
    text = models.TextField()
    filing = models.ForeignKey(Filing)
    highlighted_by = models.ForeignKey(User)
    director_name = models.TextField()
    ranges = JSONField()
    created = models.DateTimeField(default=None)
    updated = models.DateTimeField(default=None)
