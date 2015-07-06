# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DirectorFiling',
            fields=[
                ('director_id', models.TextField(serialize=False, primary_key=True, blank=True)),
                ('company', models.TextField(blank=True)),
                ('director', models.TextField(blank=True)),
                ('ticker', models.TextField(blank=True)),
                ('fy_end', models.DateField(null=True, blank=True)),
                ('gender', models.TextField(blank=True)),
                ('age', models.IntegerField(null=True, blank=True)),
                ('chairman', models.NullBooleanField()),
                ('vice_chairman', models.NullBooleanField()),
                ('lead_independent_director', models.NullBooleanField()),
                ('audit_committee_financial_expert', models.NullBooleanField()),
                ('start_date', models.DateField(null=True, blank=True)),
                ('term_end_date', models.DateField(null=True, blank=True)),
                ('tenure_yrs', models.FloatField(null=True, blank=True)),
                ('num_committees', models.IntegerField(null=True, blank=True)),
                ('committees', models.TextField(blank=True)),
                ('fileyear', models.IntegerField(null=True, blank=True)),
                ('insider_outsider_related', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'director',
            },
        ),
        migrations.CreateModel(
            name='Filing',
            fields=[
                ('folder', models.CharField(max_length=29, unique=True, serialize=False, primary_key=True)),
                ('text', models.TextField(default=None, null=True, blank=True)),
                ('type', models.CharField(default=None, max_length=7, null=True, blank=True)),
                ('text_file', models.NullBooleanField(default=None)),
            ],
        ),
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('equilar_id', models.IntegerField(null=True, blank=True)),
                ('cusip', models.TextField(null=True, blank=True)),
                ('fy_end', models.DateField(null=True, blank=True)),
                ('cik', models.IntegerField(null=True, blank=True)),
                ('file_name', models.TextField(null=True, blank=True)),
                ('date_filed', models.DateField(null=True, blank=True)),
            ],
            options={
                'db_table': 'equilar_proxies',
            },
        ),
    ]
