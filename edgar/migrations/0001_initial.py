# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Filing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('folder', models.CharField(unique=True, max_length=100)),
                ('text', models.TextField(default=b'')),
                ('html', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
