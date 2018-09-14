# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gllaunch', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HighScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scores', models.TextField()),
                ('iSession', models.ForeignKey(to='gllaunch.InteractiveSession')),
            ],
        ),
        migrations.CreateModel(
            name='InteractiveHighScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('highScore', models.SmallIntegerField(default=-1)),
                ('iSession', models.ForeignKey(to='gllaunch.InteractiveSession')),
            ],
        ),
        migrations.CreateModel(
            name='InteractiveLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.SmallIntegerField(default=1)),
                ('score', models.FloatField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('completed', models.BooleanField(default=False)),
                ('restarted', models.BooleanField(default=False)),
                ('started', models.DateTimeField()),
                ('closed', models.DateTimeField(default=None, null=True)),
                ('levelData', models.TextField(default=b'')),
            ],
        ),
        migrations.CreateModel(
            name='InteractiveLevelReload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reloads', models.SmallIntegerField(default=1)),
                ('level', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='InteractiveSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('settings', models.TextField(default=b'{"level3": true, "level1": true, "level2": true, "intro": true, "level4": true, "level5": true}')),
                ('class_id', models.CharField(max_length=220)),
            ],
        ),
        migrations.CreateModel(
            name='InteractiveState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('currentLevel', models.SmallIntegerField(default=1)),
                ('started', models.DateTimeField()),
                ('completed', models.DateTimeField(default=None, null=True)),
                ('restarted', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('customData', models.TextField(default=b'')),
                ('levels', models.SmallIntegerField()),
                ('activated_levels', models.TextField(default=None, null=True)),
                ('iSession', models.ForeignKey(to='gllaunch.InteractiveSession')),
            ],
        ),
        migrations.AddField(
            model_name='interactivelevelreload',
            name='parent',
            field=models.ForeignKey(to='datacapture.InteractiveState'),
        ),
        migrations.AddField(
            model_name='interactivelevel',
            name='parent',
            field=models.ForeignKey(to='datacapture.InteractiveState'),
        ),
    ]
