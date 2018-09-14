# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import econ.common_services.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FredCrudeOilPrices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
                ('freq', models.CharField(max_length=50)),
            ],
            bases=(models.Model, econ.common_services.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredUSRegAllFormGasPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
                ('freq', models.CharField(max_length=50)),
            ],
            bases=(models.Model, econ.common_services.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredUSRegConGasPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
                ('freq', models.CharField(max_length=50)),
            ],
            bases=(models.Model, econ.common_services.models.FredOperations),
        ),
        migrations.CreateModel(
            name='kQualsimAttempts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session_id', models.CharField(max_length=200, db_index=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'inprogress', max_length=20)),
                ('att_index', models.IntegerField(default=0)),
                ('state_data', models.TextField(default=b'{}')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='fredusregcongasprice',
            unique_together=set([('observation_date', 'observation_value', 'freq')]),
        ),
        migrations.AlterUniqueTogether(
            name='fredusregallformgasprice',
            unique_together=set([('observation_date', 'observation_value', 'freq')]),
        ),
        migrations.AlterUniqueTogether(
            name='fredcrudeoilprices',
            unique_together=set([('observation_date', 'observation_value', 'freq')]),
        ),
    ]
