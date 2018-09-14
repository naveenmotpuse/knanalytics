# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common_services', '0004_auto_20180426_0433'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kqualsimattempts',
            name='manual_update',
        ),
    ]
