# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common_services', '0005_remove_kqualsimattempts_manual_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='kqualsimattempts',
            name='manual_update',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
