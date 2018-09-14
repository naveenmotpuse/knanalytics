# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gllaunch', '0002_auto_20180106_1721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interactivesession',
            name='active',
        ),
        migrations.RemoveField(
            model_name='interactivesession',
            name='customData',
        ),
        migrations.RemoveField(
            model_name='interactivesession',
            name='end',
        ),
        migrations.RemoveField(
            model_name='interactivesession',
            name='isTest',
        ),
        migrations.RemoveField(
            model_name='interactivesession',
            name='score',
        ),
        migrations.RemoveField(
            model_name='interactivesession',
            name='start',
        ),
        migrations.RemoveField(
            model_name='interactivesession',
            name='topScore',
        ),
    ]
