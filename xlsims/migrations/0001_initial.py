# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gllaunch', '0004_auto_20180118_0222'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimsSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customData', models.TextField()),
                ('active', models.BooleanField(default=True)),
                ('isTest', models.BooleanField(default=False)),
                ('score', models.FloatField(default=-1.0)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(default=None, null=True)),
                ('topScore', models.BooleanField(default=False)),
                ('manualupdatefor', models.CharField(default=b'', max_length=220, null=True)),
                ('iSession', models.ForeignKey(to='gllaunch.InteractiveSession')),
            ],
        ),
    ]
