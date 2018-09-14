# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConsumerPriceIndex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index_name', models.CharField(max_length=64, db_index=True)),
                ('date', models.DateField()),
                ('cpi', models.DecimalField(max_digits=10, decimal_places=3)),
                ('inflation', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='InflationSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('settings', models.TextField(default=b'{"level3": true, "level1": true, "level2": true, "intro": true, "level4": true, "level5": true}')),
                ('class_id', models.CharField(max_length=220)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='consumerpriceindex',
            unique_together=set([('index_name', 'date')]),
        ),
    ]
