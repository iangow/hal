# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirror', '0002_auto_20150302_2133'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='path',
        ),
        migrations.RemoveField(
            model_name='file',
            name='site',
        ),
        migrations.DeleteModel(
            name='Site',
        ),
        migrations.AddField(
            model_name='file',
            name='remote_url',
            field=models.CharField(default=None, unique=True, max_length=200),
            preserve_default=False,
        ),
    ]
