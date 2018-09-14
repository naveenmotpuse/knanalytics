# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import econ.monetary_policy.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer_text', models.CharField(max_length=200)),
                ('status', models.BooleanField(default=False)),
                ('feedback', models.TextField(default=None, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment_text', models.CharField(max_length=200)),
                ('status', models.BooleanField(default=True)),
                ('feedback', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='FredFFRRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
            ],
            bases=(models.Model, econ.monetary_policy.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredFFTRRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
            ],
            bases=(models.Model, econ.monetary_policy.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredInflationRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
            ],
            bases=(models.Model, econ.monetary_policy.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredMoneySupplyRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
            ],
            bases=(models.Model, econ.monetary_policy.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredNaturalUERate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
            ],
            bases=(models.Model, econ.monetary_policy.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredRealGDP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
            ],
            bases=(models.Model, econ.monetary_policy.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredRealPotentialGDP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
            ],
            bases=(models.Model, econ.monetary_policy.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredTotalAssetsHeldRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
            ],
            bases=(models.Model, econ.monetary_policy.models.FredOperations),
        ),
        migrations.CreateModel(
            name='FredUERate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('observation_date', models.DateField(db_index=True)),
                ('observation_value', models.DecimalField(max_digits=10, decimal_places=3)),
            ],
            bases=(models.Model, econ.monetary_policy.models.FredOperations),
        ),
        migrations.CreateModel(
            name='GraphEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_date', models.DateField(db_index=True)),
                ('event_description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField()),
                ('value', models.CharField(max_length=20, choices=[(b'increase', b'increase'), (b'decrease', b'decrease'), (b'no_change', b'no change')])),
                ('variable', models.CharField(db_index=True, max_length=20, choices=[(b'target_indicators', b'Target/Indicators'), (b'economic_effects', b'Economic Effects'), (b'goal_variables', b'Goal Variables')])),
                ('hint_1', models.CharField(max_length=200, null=True, blank=True)),
                ('hint_2', models.CharField(max_length=200, null=True, blank=True)),
                ('comment', models.CharField(max_length=250, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MPSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('settings', models.TextField()),
                ('fed_settings', models.TextField()),
                ('class_id', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_text', models.CharField(max_length=500, db_index=True)),
                ('level', models.IntegerField(choices=[(0, b'Intro'), (1, b'Level 1'), (4, b'Level 4')])),
                ('max_attempts', models.IntegerField(default=2)),
                ('weight', models.IntegerField(default=0)),
                ('feedback', models.TextField(default=None, null=True, blank=True)),
                ('multi_choice', models.BooleanField(default=False)),
                ('option_set_count', models.IntegerField(null=True, blank=True)),
                ('extra_data', models.TextField(default=None, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(db_index=True)),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Situation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField()),
                ('overview', models.TextField()),
                ('fomc_data', models.TextField()),
                ('policy_summary', models.TextField()),
                ('intended_effects', models.TextField()),
                ('x_count', models.IntegerField(default=0)),
                ('y_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField()),
                ('mode', models.CharField(db_index=True, max_length=2, choices=[(b'E', b'Expansionary'), (b'C', b'Contractionary')])),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote_text', models.CharField(max_length=200)),
                ('status', models.BooleanField(default=True)),
                ('policy_vote', models.BooleanField(default=False)),
                ('value', models.FloatField(default=0.0)),
                ('feedback', models.TextField()),
                ('situation', models.ForeignKey(to='monetary_policy.Situation')),
            ],
        ),
        migrations.AddField(
            model_name='indicator',
            name='tool',
            field=models.ForeignKey(to='monetary_policy.Tool'),
        ),
        migrations.AlterUniqueTogether(
            name='freduerate',
            unique_together=set([('observation_date', 'observation_value')]),
        ),
        migrations.AlterUniqueTogether(
            name='fredtotalassetsheldrate',
            unique_together=set([('observation_date', 'observation_value')]),
        ),
        migrations.AlterUniqueTogether(
            name='fredrealpotentialgdp',
            unique_together=set([('observation_date', 'observation_value')]),
        ),
        migrations.AlterUniqueTogether(
            name='fredrealgdp',
            unique_together=set([('observation_date', 'observation_value')]),
        ),
        migrations.AlterUniqueTogether(
            name='frednaturaluerate',
            unique_together=set([('observation_date', 'observation_value')]),
        ),
        migrations.AlterUniqueTogether(
            name='fredmoneysupplyrate',
            unique_together=set([('observation_date', 'observation_value')]),
        ),
        migrations.AlterUniqueTogether(
            name='fredinflationrate',
            unique_together=set([('observation_date', 'observation_value')]),
        ),
        migrations.AlterUniqueTogether(
            name='fredfftrrate',
            unique_together=set([('observation_date', 'observation_value')]),
        ),
        migrations.AlterUniqueTogether(
            name='fredffrrate',
            unique_together=set([('observation_date', 'observation_value')]),
        ),
        migrations.AddField(
            model_name='comment',
            name='situation',
            field=models.ForeignKey(to='monetary_policy.Situation'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='monetary_policy.Question'),
        ),
    ]
