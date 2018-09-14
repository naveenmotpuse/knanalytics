from django.db import models
#from django.contrib.postgres.fields import JSONField
import json
import datetime


class MediaLibrary(models.Model):
    record_id = models.IntegerField(primary_key=True)
    record_title = models.TextField()
    video_url = models.TextField(default=None)
    video_thumbnail = models.TextField(default=None)
    video_creation_date = models.DateTimeField(default=None)
    video_length = models.TextField(default=None)
    metadata = models.TextField(default=None)
    recommendation = models.TextField(default=None)
    grouping = models.TextField(default=None)
    prime_video = models.TextField(default=None)
    video_info = models.TextField(default=None)
    media_mcq = models.TextField(default={})
    landing_content = models.TextField(default=None)
    landing_image = models.TextField(default=None)
    custom_target = models.TextField(default=None)
    #landingpage = models.ForeignKey('LandingPage', default=None, blank=True, null=True, on_delete=models.SET_DEFAULT)

    class Meta:
        db_table = 'MediaLibrary'

    def __str__(self):
        return str(self.record_id) + "-" + self.record_title


class MediaAsignments(models.Model):
    Id = models.AutoField(primary_key=True)
    assignment_id = models.TextField()
    custom_target = models.TextField()
    media_record_id = models.IntegerField()

    class Meta:
        db_table = 'MediaAssignments'

    def __str__(self):
        return self.custom_target + "_" + self.media_record_id


#class LandingPage(models.Model):

    #Id = models.AutoField(primary_key=True)
    #background_image = models.TextField()
    #content = models.TextField()

        #class Meta:
    #db_table = 'LandingPage'



