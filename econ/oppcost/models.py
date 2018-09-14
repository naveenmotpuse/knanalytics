from django.db import models
import json

DEFAULT_SETTINGS = {'level1': True,
                    'level2': True,
                    'level3': True
                    }


class OppCostSettings(models.Model):
    settings = models.TextField(default=json.dumps(DEFAULT_SETTINGS))
    class_id = models.CharField(max_length=220)

    @classmethod
    def getorCreateSettings(cls, class_id):
        try:
            settingsObj = cls.objects.get(class_id=class_id)
        except:
            settingsObj = cls()
            settingsObj.class_id = class_id
            settingsObj.save()
        return settingsObj