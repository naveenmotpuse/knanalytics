# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common_services', '0003_kqualsimattempts_is_binary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kqualsimattempts',
            name='is_binary',
        ),
        migrations.RemoveField(
            model_name='kqualsimattempts',
            name='state_data_binary',
        ),
        migrations.AddField(
            model_name='kqualsimattempts',
            name='manual_update',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
