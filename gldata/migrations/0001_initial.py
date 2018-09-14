# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('problem_guid', models.CharField(unique=True, max_length=80, db_index=True)),
                ('problem_data', models.TextField(default=b'{}')),
                ('correct_data', models.TextField(default=b'[]')),
            ],
        ),
        migrations.CreateModel(
            name='SessionData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_id', models.CharField(unique=True, max_length=200, db_index=True)),
                ('session_creation_date', models.DateTimeField(auto_now_add=True)),
                ('session_launch_date', models.DateTimeField(auto_now=True)),
                ('course_end_date', models.DateTimeField()),
                ('launch_mode', models.CharField(max_length=16)),
                ('launch_data', models.TextField(default=b'{}')),
                ('problem_state_data', models.TextField(default=b'{}')),
            ],
        ),
    ]
