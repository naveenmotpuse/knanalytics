# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common_services', '0006_kqualsimattempts_manual_update'),
    ]

    operations = [
        migrations.CreateModel(
            name='testdata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_id', models.CharField(max_length=200, db_index=True)),
                ('status', models.CharField(default=b'inprogress', max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='kqualsimattempts',
            name='manual_update',
        ),
    ]
