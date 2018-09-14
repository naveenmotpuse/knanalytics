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
    target_app = models.CharField(max_length=100)
    launchParam = models.TextField(default='{}')
    completed = models.BooleanField(default=False)
    
    #non persistant data
    exp = 365
    
    @classmethod
    def startInteractiveSession(cls, launchParam):

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
            
            session = InteractiveSession.objects.get(user_id=user_id, resource_id=resource_id, target_app=app)
            # if a session for the same user, assignment is expired delete it
            if timezone.now().date() > (session.started + datetime.timedelta(days=InteractiveSession.exp)).date():
                session.closed = timezone.now()
                session.save()
                raise Exception()
            session.launchParam = json.dumps(launchParam)
            if launchParam['custom_mode'] == 'do':
                session.save()
            return session
        
        except:
            
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
