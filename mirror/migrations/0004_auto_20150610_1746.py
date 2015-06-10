# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirror', '0003_auto_20150302_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Directors',
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
                'db_table': 'director"."director',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Filing',
            fields=[
                ('folder', models.CharField(max_length=29, unique=True, serialize=False, primary_key=True)),
                ('text', models.TextField(default=b'', blank=True)),
                ('type', models.CharField(default=b'', max_length=7)),
                ('text_file', models.NullBooleanField(default=None)),
            ],
        ),
        migrations.DeleteModel(
            name='File',
        ),
    ]
