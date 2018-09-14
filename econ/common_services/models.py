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

from django.db import connection


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
                                       'observation_value').filter(observation_date__range=[start_date, end_date], freq=frequency)


class FredUSRegConGasPrice(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)
    freq = models.CharField(max_length=50)

    class Meta:
        unique_together = (('observation_date', 'observation_value', 'freq'),)

    observation_type = "US Regular Conventional Gas Price"
    #frequency = "m","q","sa","a"
    frequency = "m"
    series_id = "GASREGCOVW"
    units = "lin"
    default_start_date = "1991-01-01"
    frequency_array = ["m", "q", "sa", "a"]


class FredUSRegAllFormGasPrice(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)
    freq = models.CharField(max_length=50)

    class Meta:
        unique_together = (('observation_date', 'observation_value', 'freq'),)

    observation_type = "US Regular All Formulations Gas Price"
    #frequency = "m","q","sa","a"
    frequency = "m"
    series_id = "GASREGW"
    units = "lin"
    default_start_date = "1991-01-01"
    frequency_array = ["m", "q", "sa", "a"]


class FredCrudeOilPrices(models.Model, FredOperations):
    observation_date = models.DateField(db_index=True)
    observation_value = models.DecimalField(max_digits=10, decimal_places=3)
    freq = models.CharField(max_length=50)

    class Meta:
        unique_together = (('observation_date', 'observation_value', 'freq'),)

    observation_type = "Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma"
    #frequency = "m","q","sa","a"
    frequency = "m"
    series_id = "DCOILWTICO"
    units = "lin"
    default_start_date = "1991-01-01"
    frequency_array = ["m", "q", "sa", "a"]


class QLAssignmentAdditionalDetails(models.Model):
    QL_Id = models.CharField(max_length=200,db_index=True)
    Assignment_Id = models.CharField(max_length=200,db_index=True)
    AssignmentLocation =  models.CharField(max_length=200)
    TotalScore =  models.DecimalField(max_digits=10, decimal_places=3)
    TotalUsers = models.IntegerField(default=0)
    Id = models.IntegerField(primary_key=True)

'''
    @classmethod
    def getClassAverageScore(cls, qlid, asgnid, maxscore, score):
	sql_query = """SELECT QL_Id, Assignment_Id, TotalScore FROM common_services_qlassignmentadditionaldetails
        WHERE QL_Id=%s and Assignment_Id=%s"""
        adddetails = cls.objects.raw(sql_query, [qlid, asgnid])
        if(sum(1 for result in adddetails) > 0):
            if(score!=-1):  # user had better score or its first attempt
                if(maxscore==-1):
                    #Update score and user count -- user's first attempt.
                    sql_updatequery = """UPDATE common_services_qlassignmentadditionaldetails 
                    SET TotalScore = (TotalScore + %s),  TotalUsers = (TotalUsers + %s) WHERE QL_Id=%s and Assignment_Id=%s"""
                    cursor.execute(
                        sql_updatequery, (score, 1, qlid, asgnid))
                    
                else: 
                    #update score different only -- user's next attempt with better score
                    sql_updatequery = """UPDATE common_services_qlassignmentadditionaldetails 
                    SET TotalScore = (TotalScore + %s) WHERE QL_Id=%s and Assignment_Id=%s"""
                    cursor.execute(
                        sql_updatequery, (score, qlid, asgnid))
                    
        else: 
            #Insert New Record
            sql_insertcommand = """INSERT INTO common_services_qlassignmentadditionaldetails 
                    (QL_Id, Assignment_Id, AssignmentLocation, TotalScore, TotalUsers) VALUES (%s, %s, %s, %s, %s)"""
            with connection.cursor() as cursor:
                cursor.execute(sql_insertcommand, (qlid, asgnid, '', score, 1))

        #get average score
        sql_query = """SELECT (TotalScore/TotalUsers) as AvgScore FROM common_services_qlassignmentadditionaldetails
        WHERE QL_Id=%s and Assignment_Id=%s"""
        scoredetail = cls.objects.raw(sql_query, [qlid, asgnid])
	avgscore = 0
        if(sum(1 for result in scoredetail) > 0):
            avgscore = scoredetail[0].AvgScore        
        
        return avgscore  
'''

class kQualsimAttempts(models.Model):
    session_id = models.CharField(max_length=200, db_index=True)
    start_date = models.DateTimeField(auto_now_add=True, editable=True)
    end_date = models.DateTimeField(auto_now=True, editable=True)
    status = models.CharField(max_length=20, default='inprogress')
    att_index = models.IntegerField(default=0)
    state_data = models.TextField(default='{}')


    @classmethod
    def createAttempt(cls, sessionId, jsonData):
        attIndex = cls.objects.filter(session_id=sessionId).count()
        session = SessionData.objects.get(session_id=sessionId)
        lnchdata = json.loads(session.launch_data)
        allatt = int(lnchdata['custom_attemptsallowed'])
        if (allatt <= 0 or (allatt > 0 and attIndex < allatt)):
            jsonDataStr = json.dumps(jsonData)
            sql_insertcommand = """INSERT INTO common_services_kqualsimattempts (session_id, start_date, end_date, status, att_index, state_data) 
            VALUES (%s, %s, %s, %s, %s,compress(%s))"""

            sql_selectcommand = """SELECT id, session_id, start_date, end_date, status, att_index, uncompress(state_data) as state_data FROM common_services_kqualsimattempts WHERE session_id=%s order by att_index desc"""

            with connection.cursor() as cursor:
                cursor.execute(sql_insertcommand, (sessionId, str(datetime.today()), str(
                    datetime.today()),'inprogress', attIndex, jsonDataStr))

                attemptsnm = cls.objects.raw(sql_selectcommand, [sessionId])

                return attemptsnm[0]

    @classmethod
    def initAttemptData(cls, sessionId, jsonData):
        trackdata = ''
        attstatus = jsonData['Attempts'][0]['status']
        trackdata = trackdata + attstatus + ',' + sessionId + ','
        try:
            sql_query = """SELECT id, status, att_index FROM common_services_kqualsimattempts 
            WHERE session_id=%s order by att_index desc"""
            attempts = cls.objects.raw(sql_query, [sessionId])
            if(sum(1 for result in attempts) > 0):
                attempt = attempts[0]
                if(attempt.status == 'complete'):
                    cls.createAttempt(sessionId, jsonData)
                    trackdata = trackdata + 'create new,'
                else:
                    with connection.cursor() as cursor:
                        jsonDataStr = json.dumps(jsonData)
                        sql_query = """UPDATE common_services_kqualsimattempts 
                        SET state_data=compress(%s),status=%s, end_date=%s WHERE id=%s"""
                        cursor.execute(
                            sql_query, (json.dumps(jsonData), attstatus, str(datetime.today()), attempt.id))

                    trackdata = trackdata + 'update existing,'
            else:
                cls.createAttempt(sessionId, jsonData)
                trackdata = trackdata + 'count0 create new1,'

            return trackdata
        except Exception as e:
            cls.createAttempt(sessionId, jsonData)
            return trackdata + ' Exception:' + str(e) + '- create new2'

    @classmethod
    def saveAttemptData(cls, sessionId, jsonData):
        trackdata = ''
        attstatus = jsonData['Attempts'][0]['status']
        trackdata = trackdata + attstatus + ',' + sessionId + ','
        try:
            #attempts = cls.objects.filter(session_id=sessionId)
            sql_query = """SELECT id, status, att_index 
            FROM common_services_kqualsimattempts WHERE session_id=%s order by att_index desc"""
            attempts = cls.objects.raw(sql_query, [sessionId])
            if(sum(1 for result in attempts) > 0):
                attmpt = attempts[0]

                if(attmpt.status != 'complete'):
                    #dbjsondata = json.loads(attmpt.state_data)
                    sql_query = """SELECT id, uncompress(state_data) as state_data 
                    FROM common_services_kqualsimattempts WHERE id=%s"""
                    attemptsnm = cls.objects.raw(sql_query, [attmpt.id])
                    #trackdata = trackdata + attemptsnm[0].state_data
                    dbjsondata = json.loads(attemptsnm[0].state_data)

                    trackdata = trackdata + 'json.loads ,'
                    dbreqno = 0
                    currreqno = 0
                    if dbjsondata.get('Attempts') and dbjsondata['Attempts'][0].get('requestNo'):
                        dbreqno = dbjsondata['Attempts'][0]['requestNo']

                    if jsonData.get('Attempts') and jsonData['Attempts'][0].get('requestNo'):
                        currreqno = jsonData['Attempts'][0]['requestNo']

                    if (dbreqno <= currreqno):
                        sql_query = """UPDATE common_services_kqualsimattempts 
                        SET state_data=compress(%s), status=%s, end_date=%s WHERE id=%s"""
                        jsonDataStr = json.dumps(jsonData)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                sql_query, (json.dumps(jsonData), attstatus, str(datetime.today()), attmpt.id))
            else:
                trackdata = trackdata + 'count > 0 else'

            return trackdata
        except Exception as e:
            return trackdata + 'exception occure:' + str(e)

    @classmethod
    def getAttemptData(cls, sessionId, attIndex=0):
        try:
            sql_query = """SELECT id, session_id, start_date, end_date, status, att_index, uncompress(state_data) as state_data 
            FROM common_services_kqualsimattempts WHERE session_id=%s AND att_index=%s"""
            attempts = cls.objects.raw(sql_query, [sessionId, attIndex])
            if(sum(1 for result in attempts) > 0):
                return attempts[0]
            else:
                return {}
        except:
            return {}

    @classmethod
    def getLastAttemptData(cls, sessionId):
        errorobj = {}
        errorobj["tracedata"] = ""
        try:
            #attempts = cls.objects.filter(session_id=sessionId)
            sql_query = """SELECT id, session_id, start_date, end_date, status, att_index, uncompress(state_data) as state_data 
            FROM common_services_kqualsimattempts WHERE session_id=%s order by att_index desc"""
            attempts = cls.objects.raw(sql_query, [sessionId])
            if(sum(1 for result in attempts) > 0):
                errorobj["tracedata"] += str(sum(1 for result in attempts))
                return attempts[0]
            else:
                errorobj["tracedata"] += "inside else"
                attIndex = cls.objects.filter(session_id=sessionId).count()
                with connection.cursor() as cursor:
                    sql_query = """INSERT INTO common_services_kqualsimattempts (session_id, start_date, end_date, status, att_index, state_data) 
                    VALUES (%s,%s,%s,%s,%s,compress(%s))"""
                    cursor.execute(sql_query, (sessionId, str(datetime.today()), str(
                        datetime.today()), 'inprogress', attIndex, '{}'))

                    sql_query = """SELECT id, session_id, start_date, end_date, status, att_index, uncompress(state_data) as state_data 
                    FROM common_services_kqualsimattempts WHERE session_id=%s order by att_index desc"""

                    errorobj["tracedata"] += "inside else after select"
                    attempt = cls.objects.raw(sql_query, [sessionId])
                    return attempt[0]

        except Exception as e:
            errorobj["tracedata"] += str(e)
            return errorobj

    @classmethod
    def getAllAttemptData(cls, sessionId, pstatus):
        #attempts = cls.objects.filter(session_id=sessionId, status=pstatus)
        sql_query = """SELECT id, session_id, start_date, end_date, status, att_index, uncompress(state_data) as state_data 
        FROM common_services_kqualsimattempts WHERE session_id=%s AND status=%s order by att_index desc"""
        attempts = cls.objects.raw(sql_query, [sessionId, pstatus])
        if(sum(1 for result in attempts) > 0):
            return attempts
        else:
            return []

    @classmethod
    def getAttemptCount(cls, sessionId, pstatus):
        return cls.objects.filter(session_id=sessionId, status=pstatus).count()


class testdata(models.Model):
    session_id = models.CharField(max_length=200, db_index=True)
    status = models.CharField(max_length=20, default='inprogress')

# end of file


