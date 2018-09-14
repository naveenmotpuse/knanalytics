from django.db import models
import json
import datetime
from django.utils import timezone 
from django.conf import settings
import uuid


class InteractiveSession(models.Model):
    started = models.DateTimeField(auto_now=True)
    closed = models.DateTimeField(default=None, null=True)
    user_id = models.CharField(max_length=220, db_index=True)
    resource_id = models.CharField(max_length=220, db_index=True)
    context_id = models.CharField(max_length=220, db_index=True)
    target_app = models.CharField(max_length=220)
    launchParam = models.TextField(default='{}')
    completed = models.BooleanField(default=False)
    
    #non persistant data
    exp = 365

    @classmethod
    def getSessionObjectFromJson(cls, jsession):
        try:
            sessionobj = InteractiveSession.objects.get(user_id=jsession["user_id"], resource_id=jsession["resource_id"], target_app=jsession["target_app"],context_id = jsession["context_id"])
        except:
            sessionobj = InteractiveSession();
            #launch parameters that will also double as search parameters
            sessionobj.user_id = jsession["user_id"]
            sessionobj.resource_id = jsession["resource_id"]
            sessionobj.context_id = jsession["context_id"]
            sessionobj.target_app = jsession["target_app"]
            sessionobj.launchParam = json.dumps(jsession["launchParam"])
            sessionobj.started = timezone.now()
            sessionobj.save();
        
        return sessionobj
    
    @classmethod
    def startInteractiveSession(cls, launchParam):
	print "nm-startInterctive session start"
        user_id = launchParam['user_id']
        if launchParam['custom_mode'] == 'preview' or launchParam['custom_mode'] == 'practice':
            try:
                resource_id = launchParam['custom_resource_id']
            except:
                resource_id = 'unassigned';
                launchParam['custom_resource_id'] = resource_id;
        else:
            resource_id = launchParam['custom_resource_id'];
            
        context_id = launchParam['context_id']
        app = launchParam['custom_target_' + launchParam['custom_currentquestion']]
        
        try:
            print "nm-startinteractivesession-- inside try-- user_id:" + user_id + " resource_id:" + resource_id + " target_app" + app
            #session = InteractiveSession.objects.get(user_id=user_id, resource_id=resource_id, target_app=app)
	    session = InteractiveSession.objects.filter(user_id=user_id, resource_id=resource_id, target_app=app)
            if len(session) == 0 :
		raise Exception()
	    else:
		session = session[0]
	    # if a session for the same user, assignment is expired delete it
	    print "nm-timecondition" + str(timezone.now().date() > (session.started + datetime.timedelta(days=InteractiveSession.exp)).date())
            if timezone.now().date() > (session.started + datetime.timedelta(days=InteractiveSession.exp)).date():
		print "inside time condition"
                session.closed = timezone.now()
                session.save()
                raise Exception()
            session.launchParam = json.dumps(launchParam)
            if launchParam['custom_mode'] == 'do':
                session.save()
            return session
        
        except Exception, e:
            print "nm-startinteractivesesion -- inside catch - error:" + str(e)
            session = InteractiveSession();
            #launch parameters that will also double as search parameters
            session.user_id = launchParam['user_id']
            session.resource_id = launchParam['custom_resource_id']
            session.context_id = launchParam['context_id']
            session.target_app = app
            session.launchParam = json.dumps(launchParam)
            session.started = timezone.now()
            session.save();
            try:
                if settings.LEVEL_LOCK:
                    lock = LevelLock(session=session, level=launchParam['lock_level'])
                    lock.save()
            except:
                pass
        return session;

    @classmethod
    def completeInteractiveSession(cls, session, completed=True):
        session.completed = completed
        session.close = timezone.now()
        session.save()

    def getLaunchParam(self):
        try:
            return self.paramDict
        except:
            self.paramDict = json.loads(self.launchParam)
            return self.paramDict
    
class TPI_Launch_Log(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    
    @classmethod
    def logTPIRequest(cls, request):
        
        logValues = []
        logValues.append('TPI Tool Launch request received:')
        logValues.append("request path : " + request.path)
        for k,v in request.POST.items():
            logValues.append('\t' + k + ':' + v)
        msg = TPI_Launch_Log()
        msg.message = '\n'.join(logValues)
        msg.save()

class LevelLock(models.Model):
    session = models.ForeignKey(InteractiveSession)
    level = models.SmallIntegerField()
    

        
         


# Create your models here.
