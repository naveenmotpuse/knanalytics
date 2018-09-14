

import datetime
import decimal
from django.db import models
import requests
import json


DEFAULT_LEVEL_SETTINGS = {'intro': True,
                          'level1': True,
                          'level2': True,
                          'level3': True,
                          'level4': True,
                          'level5': True
                          }


class ConsumerPriceIndex(models.Model):
    index_name = models.CharField(max_length=64, db_index=True)
    date = models.DateField()
    cpi = models.DecimalField(max_digits=10, decimal_places=3)
    inflation = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = (('index_name', 'date'))

    urlBase = 'https://research.stlouisfed.org/fred2/data/'

    CPI_DATA_URLS = {
        'cpiUsAll': 'CPIAUCSL.txt',
        'cpiUsAllUnadjusted': 'USACPIALLMINMEI.txt',
        'cpiUsApparel': 'CPIAPPSL.txt',
        'cpiUsCore': 'CPILFESL.txt',
        'cpiUsEduAndCom': 'CPIEDUSL.txt',
        'cpiUsFood': 'CPIFABSL.txt',
        'cpiUsHousing': 'CPIHOSSL.txt',
        'cpiUsMedical': 'CPIMEDSL.txt',
        'cpiUsOther': 'CPIOGSSL.txt',
        'cpiUsRecreation': 'CPIRECSL.txt',
        'cpiUsTransport': 'CPITRNSL.txt',
        'cpiBrasil': 'BRACPIALLMINMEI.txt',
        'cpiCanada': 'CANCPIALLMINMEI.txt',
        'cpiChile': 'CHLCPIALLMINMEI.txt',
        'cpiChina': 'CHNCPIALLMINMEI.txt',
        'cpiEuroZone': 'CPHPTT01EZM661N.txt',
        'cpiFrance': 'FRACPIALLMINMEI.txt',
        'cpiGermany': 'DEUCPIALLMINMEI.txt',
        'cpiIndia': 'INDCPIALLMINMEI.txt',
        'cpiIndonesia': 'IDNCPIALLMINMEI.txt',
        'cpiItaly': 'ITACPIALLMINMEI.txt',
        'cpiJapan': 'JPNCPIALLMINMEI.txt',
        'cpiMexico': 'MEXCPIALLMINMEI.txt',
        'cpiRussia': 'RUSCPIALLMINMEI.txt',
        'cpiSouthKorea': 'KORCPIALLMINMEI.txt',
        'cpiSpain': 'ESPCPIALLMINMEI.txt',
        'cpiTurkey': 'TURCPIALLMINMEI.txt',
        'cpiUK': 'GBRCPIALLMINMEI.txt',
    }

    @classmethod
    def fetchCpiData(cls):
        for item in cls.CPI_DATA_URLS.items():
            index_name = item[0]
            url = cls.urlBase + item[1]
            response = requests.get(url, stream=True)
            try:
                response.raise_for_status()
            except Exception as e:
                print '%s: %s: %s' % (index_name, url, e)
                continue
            cls.objects.filter(index_name=index_name).delete()
            objects = {}
            for line in response.iter_lines():
                tokens = line.split()
                if len(tokens) != 2:
                    continue
                obj = cls(index_name=index_name)
                try:
                    obj.date = datetime.datetime.strptime(tokens[0], '%Y-%m-%d').date()
                    obj.cpi = decimal.Decimal(tokens[1])
                except Exception as e:
                    continue
                whence = datetime.date(obj.date.year - 1, obj.date.month, obj.date.day)                    
                if whence in objects:
                    previous_cpi = objects[whence].cpi
                    try:
                        obj.inflation = decimal.Decimal(
                            decimal.Decimal('100.0') * (obj.cpi - previous_cpi) / previous_cpi
                        )
                    except:
                        obj.inflation = decimal.Decimal('0.0')
                else:
                    obj.inflation = decimal.Decimal('0.0')
                objects[obj.date] = obj
            cls.objects.bulk_create(objects.values())

    @classmethod
    def getCpiData(cls, index_names=[], start_date=None, end_date=None):
        if len(index_names) == 0:
            index_names = cls.CPI_DATA_URLS.keys()
        if not start_date:
            start_date = datetime.date.min
        if not end_date:
            end_date = datetime.date.max
        result = {}
        for index_name in index_names:
            result[index_name] = []
        for obj in cls.objects.filter(index_name__in=index_names,
                                      date__gte=start_date,
                                      date__lte=end_date
                                      ).order_by('date').all():#.select_related("index_name").order_by('date'):
            result[obj.index_name].append({
                                           'date': obj.date.isoformat(),
                                           'cpi': float(obj.cpi),
                                           'inflation': float(obj.inflation)
                                           })
        return result


class InflationSettings(models.Model):
    settings = models.TextField(default=json.dumps(DEFAULT_LEVEL_SETTINGS))
    class_id = models.CharField(max_length=220)

    @classmethod
    def getOrCreateSettings(cls, class_id):
        try:
            return cls.objects.get(class_id=class_id)
        except:
            return cls.objects.create(class_id=class_id)





