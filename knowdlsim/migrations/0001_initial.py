# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RevelActivities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activityId', models.CharField(max_length=120, db_index=True)),
                ('activityType', models.CharField(max_length=120)),
                ('subType', models.CharField(max_length=120)),
                ('seq', models.IntegerField(default=-1)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('gradable', models.BooleanField(default=False)),
                ('metadata', models.TextField(default=b'{}')),
                ('assignmentId', models.CharField(max_length=120, db_index=True)),
                ('courseId', models.CharField(max_length=120, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='RevelAssignmentDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assignmentId', models.CharField(max_length=120, db_index=True)),
                ('templateId', models.CharField(max_length=120, db_index=True)),
                ('courseId', models.CharField(max_length=120, db_index=True)),
                ('totalScore', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('numOfUsers', models.IntegerField(default=0)),
                ('settingsData', models.TextField()),
                ('objectiveDetails', models.TextField(default=None, null=True)),
                ('status', models.BooleanField(default=True)),
                ('createDate', models.DateTimeField(auto_now_add=True)),
                ('lastUpdateDate', models.DateTimeField(auto_now_add=True)),
                ('lastUpdateFor', models.CharField(default=b'', max_length=200, null=True)),
                ('additionalField1', models.TextField(default=b'', null=True)),
                ('additionalField2', models.TextField(default=b'', null=True)),
                ('additionalField3', models.TextField(default=b'', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RevelAssignments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('assignmentId', models.CharField(max_length=120, db_index=True)),
                ('assignmentType', models.CharField(max_length=120)),
                ('title', models.TextField(default=b'')),
                ('description', models.TextField(default=b'')),
                ('templateId', models.CharField(max_length=120, db_index=True)),
                ('courseId', models.CharField(max_length=120, db_index=True)),
                ('dueTime', models.DateTimeField(default=None, null=True)),
                ('dueTimeUTCMilliseconds', models.CharField(max_length=20, null=True)),
                ('metadata', models.TextField(default=b'{}')),
                ('sourceCourseId', models.CharField(max_length=120)),
                ('sourceAssignmentId', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='RevelMasterAttemptData',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('assignmentId', models.CharField(max_length=120, db_index=True)),
                ('templateId', models.CharField(max_length=120, db_index=True)),
                ('courseId', models.CharField(max_length=120, db_index=True)),
                ('Student_Id', models.CharField(max_length=120, db_index=True)),
                ('StudentName', models.CharField(default=b'', max_length=200, null=True)),
                ('Role', models.CharField(default=None, max_length=120, null=True)),
                ('StartDate', models.DateTimeField(auto_now_add=True)),
                ('EndDate', models.DateTimeField(auto_now_add=True)),
                ('CompletionStatus', models.CharField(default=b'inprogress', max_length=120)),
                ('TimeSpent', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('Score', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('Points', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('ReportStatus', models.CharField(default=b'inactive', max_length=120)),
                ('stateData', models.TextField(default=b'{}')),
                ('additionalField1', models.TextField(default=b'', null=True)),
                ('additionalField2', models.TextField(default=b'', null=True)),
                ('additionalField3', models.TextField(default=b'', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RevelMasterQuestions',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('templateId', models.CharField(max_length=120, db_index=True)),
                ('courseId', models.CharField(max_length=120, db_index=True)),
                ('PageId', models.CharField(max_length=50)),
                ('QuestionId', models.CharField(max_length=100)),
                ('QuestionText', models.TextField()),
                ('Options', models.TextField()),
                ('TotalPoints', models.DecimalField(max_digits=10, decimal_places=2)),
                ('QuestionTitle', models.CharField(max_length=1000)),
                ('AdditionalInfo', models.CharField(max_length=500)),
                ('Type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='RevelQuestionAttemptDetails',
            fields=[
                ('Id', models.AutoField(serialize=False, primary_key=True)),
                ('MstAttemptId', models.IntegerField()),
                ('PageId', models.CharField(default=b'', max_length=10, null=True)),
                ('QuestionId', models.CharField(default=b'', max_length=10, null=True)),
                ('SelOptionId', models.CharField(default=b'', max_length=100, null=True)),
                ('CorrectStatus', models.CharField(default=b'', max_length=50, null=True)),
                ('Score', models.DecimalField(default=0.0, max_digits=10, decimal_places=2)),
                ('Points', models.DecimalField(default=0.0, max_digits=10, decimal_places=2)),
                ('TimeSpent', models.DecimalField(default=0.0, max_digits=10, decimal_places=2)),
                ('AdditionalInfo', models.TextField(default=b'', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RevelSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
    ]
