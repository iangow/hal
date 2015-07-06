# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mirror', '0003_auto_20150706_1020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='biographysegment',
            name='filing',
        ),
        migrations.RemoveField(
            model_name='biographysegment',
            name='highlight_ptr',
        ),
        migrations.DeleteModel(
            name='BiographySegment',
        ),
    ]
