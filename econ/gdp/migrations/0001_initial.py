# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import econ.gdp.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fred_ContriesGDPData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=20, decimal_places=3)),
                ('freq', models.CharField(max_length=50)),
                ('seriesid', models.CharField(max_length=100)),
            ],
            bases=(models.Model, econ.gdp.models.FredOperations),
        ),
        migrations.CreateModel(
            name='Fred_ContriesPOPData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=20, decimal_places=3)),
                ('freq', models.CharField(max_length=50)),
                ('seriesid', models.CharField(max_length=100)),
            ],
            bases=(models.Model, econ.gdp.models.FredOperations),
        ),
        migrations.CreateModel(
            name='Fred_StatesGDPData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=20, decimal_places=3)),
                ('freq', models.CharField(max_length=50)),
                ('seriesid', models.CharField(max_length=100)),
            ],
            bases=(models.Model, econ.gdp.models.FredOperations),
        ),
        migrations.CreateModel(
            name='Fred_StatesPOPData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=20, decimal_places=3)),
                ('freq', models.CharField(max_length=50)),
                ('seriesid', models.CharField(max_length=100)),
            ],
            bases=(models.Model, econ.gdp.models.FredOperations),
        ),
        migrations.CreateModel(
            name='Fred_TotalPOPData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=20, decimal_places=3)),
                ('freq', models.CharField(max_length=50)),
                ('seriesid', models.CharField(max_length=100)),
            ],
            bases=(models.Model, econ.gdp.models.FredOperations),
        ),
        migrations.AlterUniqueTogether(
            name='fred_totalpopdata',
            unique_together=set([('observation_date', 'observation_value', 'freq', 'seriesid')]),
        ),
        migrations.AlterUniqueTogether(
            name='fred_statespopdata',
            unique_together=set([('observation_date', 'observation_value', 'freq', 'seriesid')]),
        ),
        migrations.AlterUniqueTogether(
            name='fred_statesgdpdata',
            unique_together=set([('observation_date', 'observation_value', 'freq', 'seriesid')]),
        ),
        migrations.AlterUniqueTogether(
            name='fred_contriespopdata',
            unique_together=set([('observation_date', 'observation_value', 'freq', 'seriesid')]),
        ),
        migrations.AlterUniqueTogether(
            name='fred_contriesgdpdata',
            unique_together=set([('observation_date', 'observation_value', 'freq', 'seriesid')]),
        ),
    ]
