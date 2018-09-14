# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommonSPData',
            fields=[
                ('Id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('Column1', models.TextField()),
                ('Column2', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TMSettingsDetails',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('ModuleId', models.CharField(max_length=500)),
                ('AssignmentId', models.CharField(max_length=500)),
                ('MaxStudents', models.IntegerField()),
                ('PollingResult', models.CharField(max_length=250)),
                ('TimeLimit', models.IntegerField()),
                ('TimeLimitUnit', models.CharField(max_length=50)),
                ('TeamScore', models.IntegerField()),
                ('StudentScore', models.IntegerField()),
            ],
            options={
                'db_table': 'tmsettingsdetails',
            },
        ),
        migrations.CreateModel(
            name='TMStudentDetails',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('FirstName', models.CharField(max_length=250)),
                ('LastName', models.CharField(max_length=250)),
                ('Email', models.CharField(max_length=500)),
                ('Status', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'tmstudentdetails',
            },
        ),
        migrations.CreateModel(
            name='TMStudentScore',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('ModuleId', models.CharField(max_length=500)),
                ('AssignmentId', models.CharField(max_length=500)),
                ('StudentId', models.BigIntegerField()),
                ('DoNotShowMsgAgain', models.PositiveSmallIntegerField(default=0)),
                ('Score', models.DecimalField(null=True, max_digits=15, decimal_places=5)),
            ],
            options={
                'db_table': 'tmstudentscore',
            },
        ),
        migrations.CreateModel(
            name='TMStudQuestionResponse',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('TeamId', models.BigIntegerField()),
                ('StudentId', models.BigIntegerField()),
                ('ModuleId', models.CharField(max_length=500)),
                ('AssignmentId', models.CharField(max_length=500)),
                ('QuestionId', models.BigIntegerField()),
                ('SelectedOption', models.IntegerField()),
                ('IsQuestionAnswered', models.PositiveSmallIntegerField()),
                ('IsCorrect', models.PositiveSmallIntegerField()),
            ],
            options={
                'db_table': 'tmstudquestionsresponse',
            },
        ),
        migrations.CreateModel(
            name='TMTeamAssignments',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('ModuleId', models.CharField(max_length=500)),
                ('AssignmentId', models.CharField(max_length=500)),
                ('TeamId', models.BigIntegerField()),
                ('IsTimerStarted', models.PositiveSmallIntegerField(default=0, null=True)),
                ('TimerDate', models.DateTimeField(null=True)),
                ('TeamScore', models.DecimalField(null=True, max_digits=15, decimal_places=5)),
                ('QuestionId', models.BigIntegerField(null=True)),
            ],
            options={
                'db_table': 'tmteamassignments',
            },
        ),
        migrations.CreateModel(
            name='TMTeamDetails',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('TeamId', models.BigIntegerField()),
                ('StudentId', models.BigIntegerField()),
                ('CourseId', models.CharField(max_length=500)),
            ],
            options={
                'db_table': 'tmteamdetails',
            },
        ),
        migrations.CreateModel(
            name='TMTeams',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('Name', models.CharField(max_length=500)),
                ('CourseId', models.CharField(max_length=500)),
            ],
            options={
                'db_table': 'tmteams',
            },
        ),
    ]
