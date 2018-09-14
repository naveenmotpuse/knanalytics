# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gllaunch', '0003_auto_20180108_0449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interactivesession',
            name='target_app',
            field=models.CharField(max_length=220),
        ),
    ]
