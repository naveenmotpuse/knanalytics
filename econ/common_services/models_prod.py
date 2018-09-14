'''
Created on 15-Apr-2016

@author: naveen@knowdl.com
'''
#from _mysql import NULL
#import new
'''
Updated on 06-Feb-2017
@author: naveen@knowdl.com
Note: Updated to track Qualsim attempt data.
'''
from django.utils.deconstruct import deconstructible
import requests
import json
from django.conf import settings
from django.db import models
from datetime import datetime
import decimal
from gldata.models import SessionData

@deconstructible
class FredOperations(object):
    @classmethod
    def fetchFredData(cls):
        for frq in cls.frequency_array:
            url_base = settings.FRED_API_BASE_URL + '&series_id=%s&frequency=%s&units=%s' % (cls.series_id, frq, cls.units)
            response = requests.get(url_base, stream=True)
            if response.json().get('observations'):
                cls.objects.filter(freq=frq).delete()
                object_list = [cls(observation_date=datetime.strptime(item.get('date'), "%Y-%m-%d"),
                                   observation_value=decimal.Decimal(item.get('value')),
                                   freq=frq,
                                   ) for item in response.json().get('observations') if item.get('value') != '.']
                cls.objects.bulk_create(object_list)
                

    @classmethod
    def getFredData(cls, start_date=None, end_date=None, frequency="m"):
        if not start_date:
            start_date = cls.default_start_date
        if not end_date:
            end_date = datetime.today().strftime("%Y-%m-%d")
        return cls.objects.values_list('observation_date',
                                       'observation_value').filter(observation_date__range=[start_date, end_date],freq=frequency)


class FredUSRegConGasPrice(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)
    freq = models.CharField(max_length=50)

    class Meta:
        unique_together = (('observation_date','observation_value','freq'),)

    observation_type = "US Regular Conventional Gas Price"
    #frequency = "m","q","sa","a"
    frequency = "m"
    series_id = "GASREGCOVW"
    units = "lin"
    default_start_date = "1991-01-01"
    frequency_array = ["m","q","sa","a"]
    
class FredUSRegAllFormGasPrice(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)
    freq = models.CharField(max_length=50)

    class Meta:
        unique_together = (('observation_date','observation_value','freq'),)

    observation_type = "US Regular All Formulations Gas Price"
    #frequency = "m","q","sa","a"
    frequency = "m"
    series_id = "GASREGW"
    units = "lin"
    default_start_date = "1991-01-01"
    frequency_array = ["m","q","sa","a"]

class FredCrudeOilPrices(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)
    freq = models.CharField(max_length=50)

    class Meta:
        unique_together = (('observation_date','observation_value','freq'),)

    observation_type = "Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma"
    #frequency = "m","q","sa","a"
    frequency = "m"
    series_id = "DCOILWTICO"
    units = "lin"
    default_start_date = "1991-01-01"
    frequency_array = ["m","q","sa","a"]



class kQualsimAttempts(models.Model):   
    session_id = models.CharField(max_length=200, db_index=True) 
    start_date = models.DateTimeField(auto_now_add=True, editable=True)
    end_date = models.DateTimeField(auto_now=True, editable=True)    
    status = models.CharField(max_length=20,default='inprogress')
    att_index = models.IntegerField(default=0)
    state_data = models.TextField(default="{}")
    
    
    @classmethod
    def createAttempt(cls,sessionId,jsonData):
        attIndex = cls.objects.filter(session_id=sessionId).count()      
        session = SessionData.objects.get(session_id=sessionId) 
        lnchdata = json.loads(session.launch_data)        
        allatt = int(lnchdata['custom_attemptsallowed'])
        if (allatt <= 0 or (allatt>0 and attIndex < allatt)):         
            attempt = cls.objects.create(session_id=sessionId, start_date = datetime.today(), end_date = datetime.today(),
                                             status = 'inprogress', att_index=attIndex,state_data=json.dumps(jsonData)                                         
                                             )
            attempt.save()        
            return attempt  
    
    @classmethod
    def initAttemptData(cls, sessionId, jsonData): 
        trackdata = ''
        attstatus = jsonData['Attempts'][0]['status']
        trackdata = trackdata + attstatus + ',' + sessionId + ','             
        try:
            attempts = cls.objects.filter(session_id=sessionId)
            trackdata = trackdata + 'count:' + str(attempts.count()) + ','
            if(attempts.count()>0):
                attempt = attempts.order_by('-att_index')[0]
                trackdata = trackdata + 'dbstatus:' + attempt.status + ','
                if(attempt.status == 'complete'):
                    cls.createAttempt(sessionId, jsonData)  
                    trackdata = trackdata + 'create new,'
                else:
                    attempt.state_data=json.dumps(jsonData)  
                    attempt.status = attstatus   
                    attempt.end_date = datetime.today()                    
                    attempt.save()
                    trackdata = trackdata + 'update existing,'
            else:
                cls.createAttempt(sessionId, jsonData) 
                trackdata = trackdata + 'count0 create new1,'
                
            return trackdata
        except Exception, e:
            cls.createAttempt(sessionId, jsonData)
            return trackdata + ' Exception:' + str(e) + '- create new2'
            
    @classmethod
    def saveAttemptData(cls, sessionId, jsonData): 
        trackdata = ''
        attstatus = jsonData['Attempts'][0]['status']  
        trackdata = trackdata + attstatus + ',' + sessionId + ','          
        try:
            attempts = cls.objects.filter(session_id=sessionId)
            trackdata = trackdata + 'count:' + str(attempts.count()) + ','
            if(attempts.count()>0):
                attmpt = attempts.order_by('-att_index')[0]
                if(attmpt.status != 'complete'):  
                    dbjsondata = json.loads(attmpt.state_data)
                    trackdata = trackdata + 'json.loads ,'
                    dbreqno=0
                    currreqno=0
                    trackdata = trackdata + 'dbreq:' + str(dbreqno) + ', currreq:' + str(currreqno) +','
                    if dbjsondata.get('Attempts') and dbjsondata['Attempts'][0].get('requestNo'):                    
                        dbreqno = dbjsondata['Attempts'][0]['requestNo'] 
                    
                    if jsonData.get('Attempts') and jsonData['Attempts'][0].get('requestNo'):                    
                        currreqno = jsonData['Attempts'][0]['requestNo']
                    
                    trackdata = trackdata +'dbreq1:' + str(dbreqno) + ', currreq1:' + str(currreqno) +','
                    if (dbreqno <= currreqno):    
                        trackdata = trackdata + 'inside if, dbstatus:' + attmpt.status + ', cuustatus:' + attstatus
                        attmpt.state_data=json.dumps(jsonData)  
                        attmpt.status = attstatus   
                        attmpt.end_date = datetime.today()                
                        attmpt.save()
            else:
                trackdata = trackdata + 'count > 0 else'
                    
            return trackdata
        except Exception, e:            
            return trackdata + 'exception occure:' + str(e)
         
            
    @classmethod
    def getAttemptData(cls,sessionId,attIndex=0):
        try:
            attempts = cls.objects.filter(session_id=sessionId,att_index = attIndex)
            if(attempts.count()>0):
                return attempts[0]
            else:
                return {}
        except:
            return {}
        
    
    @classmethod
    def getLastAttemptData(cls,sessionId):
        try:
            attempts = cls.objects.filter(session_id=sessionId)
            if(attempts.count()>0):
                attempt = attempts.order_by('-att_index')[0]
                return attempt
            else:
                attIndex = cls.objects.filter(session_id=sessionId).count()        
                attempt = cls.objects.create(session_id=sessionId, start_date = datetime.today(), end_date = datetime.today(),
                                                 status = 'inprogress', att_index=attIndex                                        
                                                 )
                attempt.save()        
                return attempt              
        except:
            return {}
        
    @classmethod
    def getAllAttemptData(cls,sessionId,pstatus):        
        attempts = cls.objects.filter(session_id=sessionId, status=pstatus)
        if(attempts.count()>0):
            return attempts.order_by('att_index')
        else:
            return []
    
    @classmethod
    def getAttemptCount(cls,sessionId,pstatus):        
        attempts = cls.objects.filter(session_id=sessionId, status=pstatus)
        return attempts.count()


# end of file








