# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mirror', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Highlight',
            fields=[
                ('id', models.TextField(unique=True, serialize=False, editable=False, primary_key=True)),
                ('uri', models.TextField()),
                ('quote', models.TextField()),
                ('text', models.TextField()),
                ('ranges', jsonfield.fields.JSONField()),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='BiographySegment',
            fields=[
                ('highlight_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='mirror.Highlight')),
                ('filing', models.ForeignKey(editable=False, to='mirror.Filing')),
            ],
            bases=('mirror.highlight',),
        ),
        migrations.AddField(
            model_name='highlight',
            name='highlighted_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
