# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('mirror', '0002_auto_20150706_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='highlight',
            name='highlighted_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
