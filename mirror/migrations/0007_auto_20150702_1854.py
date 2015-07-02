# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirror', '0006_biographysegment'),
    ]

    operations = [
        migrations.AddField(
            model_name='biographysegment',
            name='created',
            field=models.DateTimeField(default=None),
        ),
        migrations.AddField(
            model_name='biographysegment',
            name='updated',
            field=models.DateTimeField(default=None),
        ),
    ]
