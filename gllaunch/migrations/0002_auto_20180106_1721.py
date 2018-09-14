# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('gllaunch', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='interactivesession',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='interactivesession',
            name='customData',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='interactivesession',
            name='end',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='interactivesession',
            name='isTest',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='interactivesession',
            name='score',
            field=models.FloatField(default=-1.0),
        ),
        migrations.AddField(
            model_name='interactivesession',
            name='start',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 6, 23, 20, 57, 869706, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='interactivesession',
            name='topScore',
            field=models.BooleanField(default=False),
        ),
    ]
