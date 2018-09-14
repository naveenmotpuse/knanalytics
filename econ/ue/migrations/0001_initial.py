# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FredUnemploymentData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(max_length=10, db_index=True)),
                ('data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='UESettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('settings', models.TextField(default=b'{"useNaturalRate": true, "levels": "all"}')),
                ('class_id', models.CharField(max_length=220)),
            ],
        ),
    ]
