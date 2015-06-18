# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirror', '0004_auto_20150610_1746'),
    ]

    operations = [
        migrations.CreateModel(
            name='Biography',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('director_name', models.TextField()),
                ('text', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='filing',
            name='text',
            field=models.TextField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='filing',
            name='type',
            field=models.CharField(default=None, max_length=7, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='biography',
            name='filing',
            field=models.ForeignKey(to='mirror.Filing'),
        ),
        migrations.AlterUniqueTogether(
            name='biography',
            unique_together=set([('filing', 'director_name')]),
        ),
    ]
