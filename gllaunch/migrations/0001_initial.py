# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InteractiveSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started', models.DateTimeField(auto_now=True)),
                ('closed', models.DateTimeField(default=None, null=True)),
                ('user_id', models.CharField(max_length=220, db_index=True)),
                ('resource_id', models.CharField(max_length=220, db_index=True)),
                ('context_id', models.CharField(max_length=220, db_index=True)),
                ('target_app', models.CharField(max_length=100)),
                ('launchParam', models.TextField(default=b'{}')),
                ('completed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='LevelLock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.SmallIntegerField()),
                ('session', models.ForeignKey(to='gllaunch.InteractiveSession')),
            ],
        ),
        migrations.CreateModel(
            name='TPI_Launch_Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
