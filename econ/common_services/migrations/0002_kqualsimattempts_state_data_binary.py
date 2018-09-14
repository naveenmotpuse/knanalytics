# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common_services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kqualsimattempts',
            name='state_data_binary',
            field=models.BinaryField(default=b''),
        ),
    ]
