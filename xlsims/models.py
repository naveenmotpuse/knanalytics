
from django.db import models
from django.utils import timezone 
from gllaunch.models import InteractiveSession

class SimsSession(models.Model):
    iSession = models.ForeignKey(InteractiveSession);
    customData = models.TextField()
    active = models.BooleanField(default=True)
    isTest = models.BooleanField(default=False)
    
    #state variables for attempt count, duration, and score
    score = models.FloatField(default=-1.0)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, default=None)
    topScore = models.BooleanField(default=False)
    manualupdatefor = models.CharField(max_length=220,default='',null=True)

    @classmethod
    def getSimSessionObjectFromJson(cls, jsimsession):
        try:
	    #print "naveen get sim session - start1: user_id=" + jsimsession["iSession"]["user_id"] + " resource_id=" + jsimsession["iSession"]["resource_id"] + " target_app=" + jsimsession["iSession"]["target_app"] + " context_id=" + jsimsession["iSession"]["context_id"]
            sessionobj = InteractiveSession.objects.filter(user_id=jsimsession["iSession"]["user_id"], resource_id=jsimsession["iSession"]["resource_id"], target_app=jsimsession["iSession"]["target_app"],context_id = jsimsession["iSession"]["context_id"]).order_by("-started")[:1].get()
	    #print "naveen get sim session - sessionobj:" +  sessionobj.user_id
            simsessionobj = SimsSession.objects.filter(iSession=sessionobj, active=True).order_by("-start")[:1].get()
	    #print "naveen get sim session - simsessionobj success:"
        except Exception, e:
	    #print "naveen get sim session - exception - create new " + "error:" + str(e)
            simsessionobj = SimsSession();
            #launch parameters that will also double as search parameters
            simsessionobj.iSession = sessionobj
            simsessionobj.customData = jsimsession["customData"]
            simsessionobj.active = jsimsession["active"]
            simsessionobj.isTest = jsimsession["isTest"]
            simsessionobj.score = jsimsession["score"]
            simsessionobj.start = timezone.now()
            simsessionobj.topScore = jsimsession["topScore"]
	    try:
                simsessionobj.save();
	    except Exception, innex:
		print "naveen get sim session - inner Exce" + str(innex)
	    print "naveen get sim session - top score- " + jsimsession["topScore"]
        
        return simsessionobj
    
    
