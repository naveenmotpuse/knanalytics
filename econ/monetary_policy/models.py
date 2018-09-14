

import random
import requests
from django.conf import settings
from django.db import models
from datetime import datetime
import decimal
import json
from django.utils.deconstruct import deconstructible

# Create your models here.

TOOL_MODE_CHOICES = (
    ('E', 'Expansionary'),
    ('C', 'Contractionary'),
)

LEVEL_CHOICES = (
                 (0, 'Intro'),
                 (1, 'Level 1'),
                 (4, 'Level 4'),
                )

INDICATOR_VALUE_CHOICES = (
    ('increase', 'increase'),
    ('decrease', 'decrease'),
    ('no_change', 'no change'),
)

VARIABLE_CHOICES = (
    ('target_indicators', 'Target/Indicators'),
    ('economic_effects', 'Economic Effects'),
    ('goal_variables', 'Goal Variables'),
)

DEFAULT_LEVEL_SETTINGS = {"settings": [
                            {
                                "status": True,
                                "id": 0,
                                "name": "Introduction"
                            },
                            {
                                "status": True,
                                "id": 1,
                                "name": "Level1"
                            },
                            {
                                "status": True,
                                "id": 2,
                                "name": "Level2"
                            },
                            {
                                "status": True,
                                "id": 3,
                                "name": "Level3"
                            },
                            {
                                "status": True,
                                "id": 4,
                                "name": "Level4"
                            }
                            ],
                          "fed_settings": [
                                {
                                    "IWO": True,
                                    "tool": "Discount Rate",
                                    "DNI": False,
                                    "id": 0,
                                    "IWRQ": True
                                },
                                {
                                    "IWO": False,
                                    "tool": "Open Market Operations",
                                    "DNI": False,
                                    "id": 1,
                                    "IWRQ": True
                                },
                                {
                                    "IWO": False,
                                    "tool": "Required Reserve Ratio",
                                    "DNI": False,
                                    "id": 2,
                                    "IWRQ": True
                                },
                                {
                                    "IWO": False,
                                    "tool": "Interest Rate on Reserves",
                                    "DNI": False,
                                    "id": 3,
                                    "IWRQ": True
                                }
                            ]
                          }


class Indicator(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(db_index=True)
    value = models.CharField(max_length=20, choices=INDICATOR_VALUE_CHOICES)
    tool = models.ForeignKey('Tool', db_index=True)
    variable = models.CharField(db_index=True, max_length=20, choices=VARIABLE_CHOICES)
    hint_1 = models.CharField(max_length=200, blank=True, null=True)
    hint_2 = models.CharField(max_length=200, blank=True, null=True)
    comment = models.CharField(max_length=250, blank=True, null=True)

    def __unicode__(self):
        return "%s(%s)" % (self.name, self.tool)


class Tool(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(db_index=True)
    mode = models.CharField(db_index=True, max_length=2, choices=TOOL_MODE_CHOICES)

    def __unicode__(self):
        return "%s(%s)" % (self.name, self.mode)


class MPSettings(models.Model):
    settings = models.TextField()
    fed_settings = models.TextField()
    class_id = models.CharField(max_length=200)

    @classmethod
    def getOrCreateSettings(cls, class_id):
        try:
            return cls.objects.get(class_id=class_id)
        except:
            return cls.objects.create(
                  settings=json.dumps(DEFAULT_LEVEL_SETTINGS.get('settings')),
                  fed_settings=json.dumps(DEFAULT_LEVEL_SETTINGS.get('fed_settings')),
                  class_id=class_id
                  )


class Situation(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(db_index=True)
    overview = models.TextField()
    fomc_data = models.TextField()
    policy_summary = models.TextField()
    intended_effects = models.TextField()
    x_count = models.IntegerField(default=0)
    y_count = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s" % self.name


class Comment(models.Model):
    comment_text = models.CharField(max_length=200)
    situation = models.ForeignKey('Situation')
    status = models.BooleanField(default=True)
    feedback = models.TextField()

    def __unicode__(self):
        return self.comment_text


class Vote(models.Model):
    vote_text = models.CharField(max_length=200)
    situation = models.ForeignKey('Situation')
    status = models.BooleanField(default=True)
    policy_vote = models.BooleanField(default=False)
    value = models.FloatField(default=0.0)
    feedback = models.TextField()

    def __unicode__(self):
        return self.vote_text


class Answer(models.Model):
    answer_text = models.CharField(max_length=200)
    question = models.ForeignKey('Question')
    status = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True, default=None)

    def __unicode__(self):
        return self.answer_text


class Question(models.Model):
    question_text = models.CharField(db_index=True, max_length=500)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    max_attempts = models.IntegerField(default=2)
    weight = models.IntegerField(default=0)
    feedback = models.TextField(blank=True, null=True, default=None)
    multi_choice = models.BooleanField(default=False)
    option_set_count = models.IntegerField(null=True, blank=True)
    extra_data = models.TextField(blank=True, null=True, default=None)

    def __unicode__(self):
        return self.question_text

    @staticmethod
    def split_options(l, n):
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

    def get_multi_options(self):
            options = self.answer_set.all()
            option_list = []
            for option_set in Question.split_options(options, self.option_set_count):
                random.shuffle(option_set)
                option_list.append([{"optionID": option.id,
                                     "option": option.answer_text
                                     } for option in option_set])
            return option_list


@deconstructible
class FredOperations(object):
    @classmethod
    def fetchFredData(cls):
        url_base = settings.FRED_API_BASE_URL + '&series_id=%s&frequency=%s&units=%s' % (cls.series_id, cls.frequency, cls.units)
        response = requests.get(url_base, stream=True)
        if response.json().get('observations'):
            cls.objects.all().delete()
            object_list = [cls(observation_date=datetime.strptime(item.get('date'), "%Y-%m-%d"),
                               observation_value=decimal.Decimal(item.get('value'))
                               ) for item in response.json().get('observations') if item.get('value') != '.']
            cls.objects.bulk_create(object_list)

    @classmethod
    def getFredData(cls, start_date=None, end_date=None):
        if not start_date:
            start_date = cls.default_start_date
        if not end_date:
            end_date = datetime.today().strftime("%Y-%m-%d")
        return cls.objects.values_list('observation_date',
                                       'observation_value').filter(observation_date__range=[start_date, end_date])


class FredRealGDP(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = (('observation_date', 'observation_value'),)

    observation_type = "Real GDP (Millions USD)"
    frequency = "q"
    series_id = "GDPC1"
    units = "lin"
    default_start_date = "1960-01-01"


class FredRealPotentialGDP(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = (('observation_date', 'observation_value'),)

    observation_type = "Real Potential GDP"
    frequency = "q"
    series_id = "GDPPOT"
    units = "lin"
    default_start_date = "1960-01-01"


class FredInflationRate(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = (('observation_date', 'observation_value'),)

    observation_type = "Inflation Rate (Core PCE)"
    frequency = "m"
    series_id = "CPIAUCSL"
    units = "pc1"
    default_start_date = "1960-01-01"


class FredUERate(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = (('observation_date', 'observation_value'),)

    observation_type = "Unemployment Rate"
    frequency = "m"
    series_id = "UNRATE"
    units = "lin"
    default_start_date = "1960-01-01"


class FredFFRRate(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = (('observation_date', 'observation_value'),)

    observation_type = "Federal Funds Rate"
    frequency = "m"
    series_id = "FEDFUNDS"
    units = "lin"
    default_start_date = "1960-01-01"
    
#12Feb2016 - Changes to fetch Federal Funds Target Rate
class FredFFTRRate(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = (('observation_date', 'observation_value'),)

    observation_type = "Federal Funds Target Rate"
    frequency = "d"
    series_id = "DFEDTAR"
    units = "lin"
    default_start_date = "1960-01-01"


class FredMoneySupplyRate(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = (('observation_date', 'observation_value'),)

    observation_type = "Money Supply"
    frequency = "m"
    series_id = "M1SL"
    units = "lin"
    default_start_date = "1960-01-01"


class FredTotalAssetsHeldRate(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = (('observation_date', 'observation_value'),)

    observation_type = "Total Assets Held"
    frequency = "m"
    series_id = "WALCL"
    units = "lin"
    default_start_date = "2002-12-18"


class FredNaturalUERate(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = (('observation_date', 'observation_value'),)

    observation_type = "Natural Unemployment Rate"
    frequency = "q"
    series_id = "NROU"
    units = "lin"
    default_start_date = "1960-01-01"


class GraphEvent(models.Model):
    event_date = models.DateField(db_index=True)
    event_description = models.TextField()

    @classmethod
    def get_graph_events(cls, start_date="1960-01-01", end_date=None):
        if not end_date:
            end_date = datetime.today()
        graph_events = cls.objects.filter(event_date__range=[start_date,
                                                             end_date
                                                             ])
        return graph_events

    def __unicode__(self):
        return self.event_description


class Recession(models.Model):
    start_date = models.DateField(db_index=True)
    end_date = models.DateField()

    @classmethod
    def get_recession_periods(cls, start_date="1960-01-01", end_date=None):
        if not end_date:
            end_date = datetime.today()
        recession_periods = cls.objects.filter(start_date__gte=start_date,
                                               end_date__lte=end_date
                                               )
        return recession_periods

    def __unicode__(self):
        return "From %s to %s" % (datetime.strftime(self.start_date, "%m/%d/%Y"),
                                  datetime.strftime(self.end_date, "%m/%d/%Y")
                                  )



