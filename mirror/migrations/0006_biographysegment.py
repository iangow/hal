# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mirror', '0005_auto_20150618_1228'),
    ]

    operations = [
        migrations.CreateModel(
            name='BiographySegment',
            fields=[
                ('id', models.TextField(unique=True, serialize=False, primary_key=True)),
                ('text', models.TextField()),
                ('director_name', models.TextField()),
                ('ranges', jsonfield.fields.JSONField()),
                ('filing', models.ForeignKey(to='mirror.Filing')),
                ('highlighted_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
