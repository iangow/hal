from django.contrib.auth.models import User
from django.db import connection, OperationalError
from django.db import models
from jsonfield import JSONField
from sec_ftp import Client
import json
import match_directors_across_filings
import os
import re
import requests
import textwrap


_sql_path = lambda x: os.path.join(os.path.dirname(__file__), 'sql', x)


class DirectorFiling(models.Model):
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
        db_table = 'director'


class Proxy(models.Model):
    '''
    This should have a one-to-one match with filings, but, for a few
    reasons I don't want to fight with, it does not.
    '''
    equilar_id = models.IntegerField(blank=True, null=True)
    cusip = models.TextField(blank=True, null=True)
    fy_end = models.DateField(blank=True, null=True)
    cik = models.IntegerField(blank=True, null=True)
    file_name = models.TextField(blank=True, null=True)
    date_filed = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'equilar_proxies'


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
        Db._exec('load_filings.sql')
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
        with open(_sql_path('director_names.sql')) as f:
            template = f.read()
            sql = template % self.folder
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
        except OperationalError:
            cursor.execute("SELECT 'none';")
        rows = cursor.fetchall()
        names = [r[0] for r in rows]
        return sorted(list(set(names)))


def other_directorships(director_id):
    '''
    Note: director_id should look like '123.456' where 123 is the equilar_id
    of the firm and 456 is the director_id of the director within the
    firm.
    '''
    sql = '''
        WITH x AS (
            SELECT regexp_replace(b, '\..*$', '') AS equilar_id
            FROM matched_director_ids
            WHERE a='%s'
        )

        SELECT x.equilar_id, company
            FROM companies JOIN x
            ON companies.equilar_id=x.equilar_id;
        ''' % director_id
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows


class Highlight(models.Model):
    id = models.TextField(primary_key=True, unique=True, editable=False)
    uri = models.TextField()
    quote = models.TextField()
    text = models.TextField()
    ranges = JSONField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    highlighted_by = models.ForeignKey(User, null=True)

    TO_COPY = [
        'id',
        'uri',
        'quote',
        'text',
        'ranges',
        'created',
        'updated',
    ]

    @classmethod
    def create(cls, **kwargs):
        # l = kwargs['uri'].split('/')
        # folder = '/'.join(l[-2:len(l)])
        # 'filing': Filing.objects.get(folder=folder),
        try:
            user = User.objects.get(username=kwargs['username'])
        except User.DoesNotExist:
            user = None
            
        d = {
            'highlighted_by': user
        }
        for k in cls.TO_COPY:
            d[k] = kwargs[k]
        return cls.objects.create(**d)

    @classmethod
    def get_or_create(cls, **kwargs):
        try:
            return cls.objects.get(id=kwargs['id'])
        except cls.DoesNotExist:
            return cls.create(**kwargs)

    @classmethod
    def _load_highlights_for(cls, folder):
        uri = 'http://hal.marder.io/highlight/' + folder
        url = os.environ['STORE_URL'] + '/search?uri=' + uri
        response = requests.get(url)
        d = json.loads(response.content)
        for row in d['rows']:
            cls.get_or_create(**row)

    @classmethod
    def load_highlights(cls, limit=10):
        filings = Filing.objects.filter(type='DEF 14A')[0:limit]
        for f in filings:
            cls._load_highlights_for(f.folder)
            print '.'

    def clean_quote(self):
        paragraphs = re.split('\n\s+', self.quote.strip())
        f = lambda s: '\n'.join(textwrap.wrap(s))
        wrapped = map(f, paragraphs)
        return '\n\n'.join(wrapped)

    TYPES = {
        'BIO': 'BiographySegment',
    }

    def type(self):
        if '/highlight/' in self.uri:
            return self.TYPES['BIO']

    def director_name(self):
        assert self.type() == self.TYPES['BIO']
        return self.text

    def filing_id(self):
        assert self.type() == self.TYPES['BIO']
        return self.uri.replace('http://hal.marder.io/highlight/', '')

    def director_id(self, clean=True):
        sql = (
            "SELECT director_id FROM crosswalk WHERE folder='" +
            self.filing_id() +
            "' AND director='" +
            self.director_name() +
            "';"
        )
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        assert len(rows) == 1, rows
        result = rows[0][0]
        if clean:
            result = re.sub('\..*\.', '', result)
        return result


class Db(object):

    FILES = [
        'create_crosswalk.sql',
        'create_companies_table.sql',
        'load_filings.sql',
    ]

    @classmethod
    def _exec(cls, filename):
        path = _sql_path(filename)
        with open(path) as f:
            sql = f.read()
        cursor = connection.cursor()
        cursor.execute(sql)

    @classmethod
    def create_all(cls):
        Filing.sync()
        for f in cls.FILES:
            cls._exec(f)
        match_directors_across_filings.create_matched_director_ids()
