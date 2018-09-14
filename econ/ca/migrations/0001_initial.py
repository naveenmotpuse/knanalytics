# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gllaunch', '0004_auto_20180118_0222'),
    ]

    operations = [
        migrations.CreateModel(
            name='CALevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level', models.SmallIntegerField(default=1)),
                ('score', models.SmallIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('completed', models.BooleanField(default=False)),
                ('started', models.DateTimeField()),
                ('closed', models.DateTimeField(default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CARestart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('restarts', models.SmallIntegerField(default=1)),
                ('level', models.SmallIntegerField()),
                ('parent', models.ForeignKey(to='gllaunch.InteractiveSession')),
            ],
        ),
        migrations.CreateModel(
            name='CAState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('currentLevel', models.SmallIntegerField(default=1)),
                ('l1Score', models.FloatField(default=0)),
                ('l1Completed', models.DateTimeField(default=None, null=True, blank=True)),
                ('l2Score', models.FloatField(default=0)),
                ('l2Completed', models.DateTimeField(default=None, null=True, blank=True)),
                ('l3Score', models.FloatField(default=0)),
                ('l3Completed', models.DateTimeField(default=None, null=True, blank=True)),
                ('l4Score', models.FloatField(default=0)),
                ('l4Completed', models.DateTimeField(default=None, null=True, blank=True)),
                ('started', models.DateTimeField()),
                ('completed', models.DateTimeField(default=None, null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('restarted', models.BooleanField(default=False)),
                ('tool', models.CharField(default=b'none', max_length=4)),
                ('surplusWood', models.SmallIntegerField(default=0)),
                ('surplusFish', models.SmallIntegerField(default=0)),
                ('iSession', models.ForeignKey(to='gllaunch.InteractiveSession')),
            ],
        ),
        migrations.CreateModel(
            name='LevelSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('setting', models.CharField(default=b'all', max_length=10)),
                ('class_id', models.CharField(max_length=220)),
            ],
        ),
        migrations.AddField(
            model_name='calevel',
            name='parent',
            field=models.ForeignKey(to='ca.CAState'),
        ),
    ]
