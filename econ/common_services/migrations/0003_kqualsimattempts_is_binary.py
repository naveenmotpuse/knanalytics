# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common_services', '0002_kqualsimattempts_state_data_binary'),
    ]

    operations = [
        migrations.AddField(
            model_name='kqualsimattempts',
            name='is_binary',
            field=models.CharField(default=b'no', max_length=10),
        ),
    ]
