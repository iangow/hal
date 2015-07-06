# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirror', '0007_auto_20150702_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biographysegment',
            name='filing',
            field=models.ForeignKey(editable=False, to='mirror.Filing'),
        ),
        migrations.AlterField(
            model_name='biographysegment',
            name='id',
            field=models.TextField(unique=True, serialize=False, editable=False, primary_key=True),
        ),
    ]
