# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common_services', '0007_auto_20180502_0330'),
    ]

    operations = [
        migrations.CreateModel(
            name='QLAssignmentAdditionalDetails',
            fields=[
                ('QL_Id', models.CharField(max_length=200, db_index=True)),
                ('Assignment_Id', models.CharField(max_length=200, db_index=True)),
                ('AssignmentLocation', models.CharField(max_length=200)),
                ('TotalScore', models.DecimalField(max_digits=10, decimal_places=3)),
                ('TotalUsers', models.IntegerField(default=0)),
                ('Id', models.IntegerField(serialize=False, primary_key=True)),
            ],
        ),
    ]
