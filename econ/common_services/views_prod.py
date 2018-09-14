'''
Created on 15-Apr-2016

@author: naveen@knowdl.com
'''
import os
import json
import requests
import _csv
#import urllib2
import datetime
from gldata.models import SessionData
from django.http.response import HttpResponse
from econ.utils import CorsHttpDecorator
from econ.common_services.models import FredUSRegConGasPrice, FredUSRegAllFormGasPrice, FredCrudeOilPrices, kQualsimAttempts
from django.views.decorators.csrf import csrf_exempt
#from django.core.context_processors import request
from knanalytics import TPIUtils
from knowdlanalytics import models as kam

from decimal import Decimal



FRED_DB_MAP = { 
               'gasregcovw': FredUSRegConGasPrice, 
               'gasregw':FredUSRegAllFormGasPrice,
               'dcoilwtico':FredCrudeOilPrices
               }

#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_fred_data/?fred_tool_name=gasregcovw
@CorsHttpDecorator
def getFredData(request):
    
    #FredUSRegConGasPrice.fetchFredData()
    #FredUSRegAllFormGasPrice.fetchFredData()
    #FredCrudeOilPrices.fetchFredData()
    if not request.method == 'GET':
        return HttpResponse(status=400)
    
        
    try:
        fred_tool_name = request.GET['fred_tool_name']
        
    except:
        return HttpResponse(status=400)    
   
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    frequency = request.GET.get('frequency', "m")
    kwargs = {}
    if start_date:
        kwargs.update({'start_date': start_date})
    if end_date:
        kwargs.update({'end_date': end_date})
    
    kwargs.update({'frequency': frequency})
        
    model_class = FRED_DB_MAP[fred_tool_name]
    
    try:
        results = model_class.getFredData(**kwargs)        
    except:
        return HttpResponse(status=400)
    response = [[result[0].isoformat(), float(result[1])] for result in results]
    return HttpResponse(json.dumps(response),
                        status=200, content_type="application/json")


#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/save_qlsim_attempt_data
@csrf_exempt
@CorsHttpDecorator
def initAttemptData(request):
    if request.method == 'GET':
        return HttpResponse(status=400)
        
    try:
        r_data = json.loads(request.body)
        sessionId = r_data['sessionId']
        jsonData = r_data['jsonData']        
        trackdata = kQualsimAttempts.initAttemptData(sessionId, jsonData)  
              
        return HttpResponse(trackdata, status=200)   
         
    except Exception, e:
        response = HttpResponse('Error: Init attempt:'  + str(e), 404)
        return response


#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/save_qlsim_attempt_data
@csrf_exempt
@CorsHttpDecorator
def saveAttemptData(request):
    if request.method == 'GET':
        return HttpResponse(status=400)
        
    try:
        r_data = json.loads(request.body)
        sessionId = r_data['sessionId']
        jsonData = r_data['jsonData']                         
        trackdata = kQualsimAttempts.saveAttemptData(sessionId, jsonData)
        
        return HttpResponse(trackdata, status=200)  
               
    except Exception, e:
        response = HttpResponse('Error: save attempt:'  + str(e), 404)
        return response


#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_qlsim_attempt_data?sessionId=[sessionId]&attIndex=[3]
@csrf_exempt
@CorsHttpDecorator
def getAttemptData(request):   
    
    if not request.method == 'GET':
        return HttpResponse(status=400)
    
    try:
        sessionId = request.GET.get('sessionId', None)
        attIndex = request.GET.get('attIndex', None)
            
        attempt = kQualsimAttempts.getAttemptData(sessionId, attIndex)
        
        
        if hasattr(attempt, 'session_id'):
            package = {}
            package['session_id'] = attempt.session_id
            package['start_date'] = str(attempt.start_date)  
            package['end_date'] = str(attempt.end_date)  
            package['status'] = attempt.status  
            package['att_index'] = attempt.att_index  
            package['state_data'] = attempt.state_data   
            
            return HttpResponse(json.dumps(package),
                    status=200, content_type="application/json")   
        else:  
            #else condition is added to handle old data for review, before multiple attempt logic implemented.
            try:
                attempt = SessionData.objects.get(session_id=sessionId)
                lstatedata = json.loads(attempt.problem_state_data)   
                package = {}
                package['session_id'] = attempt.session_id
                package['start_date'] = str(attempt.session_creation_date)  
                package['end_date'] = str(attempt.course_end_date)   
                package['status'] = 'complete'                
                package['att_index'] = 0
                package['state_data'] = attempt.problem_state_data  
                
                duration = 0;
                if lstatedata.get('Attempts'):                
                    if lstatedata['Attempts'][0].get('duration'):
                        duration = lstatedata['Attempts'][0]['duration']                
                    #create new entry in attempt
                    attIndex = kQualsimAttempts.objects.filter(session_id=sessionId).count()        
                    attempt = kQualsimAttempts.objects.create(session_id=sessionId, start_date = datetime.datetime.today(), end_date = (datetime.datetime.today() + datetime.timedelta(seconds=duration)),
                                                     status = package['status'], att_index=attIndex,state_data=attempt.problem_state_data                                         
                                                     )
                    attempt.save()
                    #end creating new entry.
                
                return HttpResponse(json.dumps(package),
                        status=200, content_type="application/json") 
                
            except Exception, e:
                response = HttpResponse('Error: get session data:'  + str(e), 404)
                return response      
            
    except Exception, e:
        response = HttpResponse('Error: get attempt111:'  + str(e), 404)
        return response
    

#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_qlsim_lastattempt_data?sessionId=[sessionId]
@csrf_exempt
@CorsHttpDecorator
def getLastAttemptData(request):   
    
    if not request.method == 'GET':
        return HttpResponse(status=400)
    
    try:
        sessionId = request.GET.get('sessionId', None)        
        try:
            attempt = kQualsimAttempts.getLastAttemptData(sessionId) 
                
            package = {}
            package['session_id'] = attempt.session_id
            package['start_date'] = str(attempt.start_date)  
            package['end_date'] = str(attempt.end_date)  
            package['status'] = attempt.status  
            package['att_index'] = attempt.att_index  
            package['state_data'] = attempt.state_data   
            
            return HttpResponse(json.dumps(package),
                    status=200, content_type="application/json")                
                          
        except Exception, ine:
            response = HttpResponse('Error: get last attempt1==5:'  + str(ine), 404)
            return response
    except Exception, e:
        response = HttpResponse('Error: get last attempt6:'  + str(e), 404)
        return response
    
    
#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_qlsim_lastattempt_data?sessionId=[sessionId]
@csrf_exempt
@CorsHttpDecorator
def getAllAttemptData(request):   
    
    if not request.method == 'GET':
        return HttpResponse(status=400)
    
    try:
        sessionId = request.GET.get('sessionId', None)
        pstatus = request.GET.get('status', 'all')
                    
        attempts = kQualsimAttempts.objects.filter(session_id=sessionId)
        if pstatus != 'all':
            attempts = attempts.filter(status = pstatus)            
        
        lcl_list = []        
        for attmpt in attempts:                        
            lstatedata = json.loads(attmpt.state_data)             
            package = {}            
            package['session_id'] = attmpt.session_id
            package['start_date'] = str(attmpt.start_date)               
            package['end_date'] = str(attmpt.end_date)                
            package['status'] =  attmpt.status
            package['duration'] = 0            
            package['overallScore'] =0
            package['att_index'] = attmpt.att_index 
            if lstatedata.get('Attempts'):
                package['status'] = lstatedata['Attempts'][0]['status']
                if lstatedata['Attempts'][0].get('endDate'):
                    package['end_date'] = lstatedata['Attempts'][0]['endDate']
                if lstatedata['Attempts'][0].get('startDate'):                
                    package['start_date'] = lstatedata['Attempts'][0]['startDate']
                if lstatedata['Attempts'][0].get('duration'):
                    package['duration'] = lstatedata['Attempts'][0]['duration']
                if lstatedata['Attempts'][0].get('overallScore'):  
                    package['overallScore'] = lstatedata['Attempts'][0]['overallScore']    
                               
            lcl_list.append(package)
            
        return HttpResponse(json.dumps(lcl_list),
                        status=200, content_type="application/json")      
    except Exception, e:
        response = HttpResponse('Error: get all attempts:'  + str(e), 404)
        return response    

#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_qlsim_attempt_count?sessionId=[sessionId]&status=[status]
@csrf_exempt
@CorsHttpDecorator
def getAttemptCount(request):    
    if not request.method == 'GET':
        return HttpResponse(status=400)    
    try:
        sessionId = request.GET.get('sessionId', None)
        pstatus = request.GET.get('status', 'complete')
        attcount = kQualsimAttempts.getAttemptCount(sessionId, pstatus) 
                  
        return HttpResponse(attcount,status=200)
        
    except Exception, e:
        response = HttpResponse('Error: get all attempts:'  + str(e), 404)
        return response

@csrf_exempt
@CorsHttpDecorator
def NavGethttpR(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    
    response =''
    try:
        #purl = "http://api.wantedanalytics.com:7001/wantedapi/v5.0/jobs?passkey=930d854ff36911e480bfa4badbfc9e50&pagesize=0&facet={softskill,hardskill,certification,soc8}&responsetype=json&showinappropriate=false&showunclassifiedindustry=false&showunclassifiedoccupation=false&showanonymous=false"
        purl = "http://api.wantedanalytics.com:7001/wantedapi/v5.0/jobs?passkey=930d854ff36911e480bfa4badbfc9e50&pagesize=1"        
        response = HttpResponse(requests.get(url=purl,verify=False), 200)
    except Exception, e:
        response = HttpResponse('Error: wantedanalytics error: ' + str(e), 404)
                
    return response

@csrf_exempt
@CorsHttpDecorator
def getQlSimAllData(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    
    try:                    
        attempts = kQualsimAttempts.objects.order_by('session_id','att_index')             
        
        lcl_list = []        
        for attmpt in attempts:                        
            lstatedata = json.loads(attmpt.state_data)             
            package = {}            
            package['session_id'] = attmpt.session_id
            package['start_date'] = str(attmpt.start_date)               
            package['end_date'] = str(attmpt.end_date)                
            package['status'] =  attmpt.status
            package['duration'] = 0            
            package['overallScore'] =0
            package['att_index'] = attmpt.att_index 
            if lstatedata.get('Attempts'):
                package['status'] = lstatedata['Attempts'][0]['status']
                if lstatedata['Attempts'][0].get('endDate'):
                    package['end_date'] = lstatedata['Attempts'][0]['endDate']
                if lstatedata['Attempts'][0].get('startDate'):                
                    package['start_date'] = lstatedata['Attempts'][0]['startDate']
                if lstatedata['Attempts'][0].get('duration'):
                    package['duration'] = lstatedata['Attempts'][0]['duration']
                if lstatedata['Attempts'][0].get('overallScore'):  
                    package['overallScore'] = lstatedata['Attempts'][0]['overallScore']
                       
            lcl_list.append(package)
            
        return HttpResponse(json.dumps(lcl_list),
                        status=200, content_type="application/json")      
    except Exception, e:
        response = HttpResponse('Error: get all attempts:'  + str(e), 404)
        return response

#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_qlsim_short_data?idxcnt=10&sidx=0&orderby=-id
@csrf_exempt
@CorsHttpDecorator
def getQlSimShortData(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)     
     
    sidx = int(request.GET.get('sidx', 0))
    idxcnt = int(request.GET.get('idxcnt', 10)) 
    orderby = request.GET.get('orderby', '-id')   
    eidx = sidx + idxcnt
    
    try:                    
        attempts = kQualsimAttempts.objects.order_by(orderby)[sidx:eidx]
                
        package = {}            
        package['Total_Attempts'] = kQualsimAttempts.objects.count()  
        package['Total_Completed'] = kQualsimAttempts.objects.filter(status='complete').count()
        package['Total_Inprogress'] = kQualsimAttempts.objects.filter(status='inprogress').count()
        package['maxid'] = kQualsimAttempts.objects.latest("id").id
        package['Attempt_Ids'] = []
            
        for attmpt in attempts:                      
            package['Attempt_Ids'].append(attmpt.id)            
            
        return HttpResponse(json.dumps(package),
                        status=200, content_type="application/json")      
    except Exception, e:
        response = HttpResponse('Error: get all attempts:'  + str(e), 404)
        return response
    
#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_incorrect_data?plcholder=[qualsimsbusinessgoingglobalebert]
@csrf_exempt
@CorsHttpDecorator
def getQlSimIncorrectData(request):    
    if not request.method == 'GET':
        return HttpResponse(status=400)        
    plcholder = request.GET.get('plcholder', 'knowdl')
    
    try:
        attempts = kQualsimAttempts.objects.filter(session_id__icontains=plcholder).order_by('session_id')
        lcl_list = []        
        for attmpt in attempts:            
            lstatedata = json.loads(attmpt.state_data)  
            if lstatedata.get('Attempts'): 
                if lstatedata['Attempts'][0]['reqdData'].get('bookmarkData'):
                    gArrTracking = lstatedata['Attempts'][0]['reqdData']['bookmarkData']['gArrTracking']                    
                    maxScore = 0.0
                    reqUpdate = False             
                    for trackobj in gArrTracking:                                           
                        try:
                            maxScore += float(trackobj['MaxScore'])
                        except ValueError:
                            maxScore += 0.0
                        
                        d_value = trackobj['PgId']                                                       
                        if (str(d_value) == '415'):
                            d_OptId = trackobj['OptId'] 
                            d_Optscore = trackobj['OptScore'] 
                            if (float(d_Optscore)==3.0 and d_OptId == 'k-element-button41515'):
                                reqUpdate = True
                                                                            
                    
                    if reqUpdate:
                        package = {}            
                        package['session_id'] = attmpt.session_id                            
                        package['att_index'] = attmpt.att_index 
                        package['status'] = attmpt.status                        
                        package['overallScore'] = lstatedata['Attempts'][0]['overallScore']
                        package['totalScore'] = maxScore
                        package['userScore'] = lstatedata['Attempts'][0]['reqdData']['bookmarkData']['userScore']                            
                        lcl_list.append(package)
                    
        return HttpResponse(json.dumps(lcl_list),
                        status=200, content_type="application/json")      
    except Exception, e:
        response = HttpResponse('Error: getQlSimIncorrectData:'  + str(e), 404)
        return response    

#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/update_incorrect_data?plcholder=[qualsimsbusinessgoingglobalebert]
@csrf_exempt
@CorsHttpDecorator
def updateQlSimIncorrectData(request):    
    if not request.method == 'GET':
        return HttpResponse(status=400)        
    plcholder = request.GET.get('plcholder', 'knowdl')
    
    try:
        attempts = kQualsimAttempts.objects.filter(session_id__icontains=plcholder).order_by('session_id')           
        for attmpt in attempts:            
            lstatedata = json.loads(attmpt.state_data)  
            if lstatedata.get('Attempts'): 
                if lstatedata['Attempts'][0]['reqdData'].get('bookmarkData'):
                    gArrTracking = lstatedata['Attempts'][0]['reqdData']['bookmarkData']['gArrTracking']                    
                    maxScore = 0.0
                    reqUpdate = False             
                    for trackobj in gArrTracking:                                           
                        try:
                            maxScore += float(trackobj['MaxScore'])
                        except ValueError:
                            maxScore += 0.0
                        
                        d_value = trackobj['PgId']                                                       
                        if (str(d_value) == '415'):
                            d_OptId = trackobj['OptId'] 
                            d_Optscore = trackobj['OptScore'] 
                            if (float(d_Optscore)==3.0 and d_OptId == 'k-element-button41515'):
                                trackobj['OptScore'] = 5
                                reqUpdate = True                                            
                    
                    if reqUpdate:
                        userScore = float(lstatedata['Attempts'][0]['reqdData']['bookmarkData']['userScore'])                                               
                        lstatedata['Attempts'][0]['overallScore'] = ((userScore+2)/maxScore*100.0) 
                        lstatedata['Attempts'][0]['reqdData']['bookmarkData']['userScore'] = (userScore+2)
                                            
                        attmpt.state_data = json.dumps(lstatedata)
                        attmpt.save()                       
                        
                    
        return HttpResponse("success", status=200)      
    except Exception, e:
        response = HttpResponse('Error: updateQlSimIncorrectData:'  + str(e), 404)
        return response
    
#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/postgrade_incorrect_data?plcholder=[qualsimsbusinessgoingglobalebert]
@csrf_exempt
@CorsHttpDecorator
def postGradeQlSimIncorrectData(request):    
    if not request.method == 'GET':
        return HttpResponse(status=400)        
    plcholder = request.GET.get('plcholder', 'knowdl')
    
    try:
        siddict = kQualsimAttempts.objects.filter(session_id__icontains=plcholder).order_by().values_list('session_id',flat=True).distinct()        
        for sid in siddict:
            attmaxscoreacross = 0.0  
            duration = 0
            reses = kQualsimAttempts.objects.filter(status='complete', session_id = sid).order_by('session_id')
            for res in reses:
                lstatedata = json.loads(res.state_data)  
                if attmaxscoreacross <=  float(lstatedata['Attempts'][0]['overallScore']):                     
                        attmaxscoreacross = float(lstatedata['Attempts'][0]['overallScore'])
                        duration = lstatedata['Attempts'][0]['duration']    
            
            
            session = SessionData.objects.get(session_id = sid)
            launch_data = json.loads(session.launch_data)
                   
            problemNumber = launch_data['custom_currentquestion']
            problem_guid = launch_data['custom_target_' + launch_data['custom_currentquestion']] 
            targetpointstmp = launch_data['custom_points_' + launch_data['custom_currentquestion']] 
                                   
            score = attmaxscoreacross/100.0                                               
            
            targetpoints = 1.0
            try:                        
                targetpoints = float(targetpointstmp) 
            except ValueError:
                targetpoints = 1.0
                
            if targetpoints > 0.0:                            
                score = score * targetpoints
            
            score = round(score,2)                      
            
            try:
                TPIUtils.submit_outcome(launch_data, problemNumber=problemNumber, problem_guid=problem_guid, score=score, duration=duration, submissionCount=2)                
            except Exception as e:                
                pass                           
                    
        return HttpResponse("Success",
                        status=200, content_type="application/json")      
    except Exception, e:
        response = HttpResponse('Error: postGradeQlSimIncorrectData:'  + str(e), 404)
        return response    

#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/update_incorrect_data_id?sid=[qualsimsbusinessgoingglobalebert]
@csrf_exempt
@CorsHttpDecorator
def updateQlSimIncorrectDataId(request):    
    if not request.method == 'GET':
        return HttpResponse(status=400) 
           
    qssid = request.GET.get('sid', 'knowdl')
    
    try:
        attempts = kQualsimAttempts.objects.filter(session_id=qssid).order_by('session_id')
        for attmpt in attempts:            
            lstatedata = json.loads(attmpt.state_data)  
            if lstatedata.get('Attempts'): 
                if lstatedata['Attempts'][0]['reqdData'].get('bookmarkData'):
                    gArrTracking = lstatedata['Attempts'][0]['reqdData']['bookmarkData']['gArrTracking']                    
                    userScore = 0.0  
                    maxScore = 0.0 
                    reqUpdate = False             
                    for trackobj in gArrTracking: 
                        d_value = trackobj['PgId']                            
                        try:
                            userScore += float(trackobj['OptScore'])
                        except ValueError:
                            userScore += 0.0
                        
                        try:
                            maxScore += float(trackobj['MaxScore'])
                        except ValueError:
                            maxScore += 0.0
                        if str(d_value) == '225' and float(trackobj['MaxScore']==3.0):
                            trackobj['MaxScore'] = 5
                            reqUpdate = True                                                                       
                                            
                    
                    if reqUpdate:                        
                        prevAttMaxScore = float(lstatedata['Attempts'][0]['maxscore'])                        
                        lstatedata['Attempts'][0]['overallScore'] = (userScore/(maxScore +2))*100.0  
                        if prevAttMaxScore>1:
                            lstatedata['Attempts'][0]['maxscore'] = prevAttMaxScore - (prevAttMaxScore -((prevAttMaxScore/100*38)/(38+2)*100))                                     
                                              
                        attmpt.state_data = json.dumps(lstatedata)
                        attmpt.save()                       
                        
                    
        return HttpResponse("success", status=200)      
    except Exception, e:
        response = HttpResponse('Error: updateQlSimIncorrectData:'  + str(e), 404)
        return response
    
#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/postgrade_incorrect_data_id?sid=[qualsimsbusinessgoingglobalebert]
@csrf_exempt
@CorsHttpDecorator
def postGradeQlSimIncorrectDataId(request):    
    if not request.method == 'GET':
        return HttpResponse(status=400)  
          
    qssid = request.GET.get('sid', 'knowdl')
    
    try:
        siddict = kQualsimAttempts.objects.filter(session_id=qssid).order_by().values_list('session_id',flat=True).distinct()        
        for sid in siddict:
            attmaxscoreacross = 0.0  
            duration = 0
            reses = kQualsimAttempts.objects.filter(status='complete', session_id = sid).order_by('session_id')
            for res in reses:
                lstatedata = json.loads(res.state_data)  
                if attmaxscoreacross <=  float(lstatedata['Attempts'][0]['overallScore']):                     
                        attmaxscoreacross = float(lstatedata['Attempts'][0]['overallScore'])
                        duration = lstatedata['Attempts'][0]['duration']    
            
            
            session = SessionData.objects.get(session_id = sid)
            launch_data = json.loads(session.launch_data)
                   
            problemNumber = launch_data['custom_currentquestion']
            problem_guid = launch_data['custom_target_' + launch_data['custom_currentquestion']] 
            targetpointstmp = launch_data['custom_points_' + launch_data['custom_currentquestion']] 
                                   
            score = attmaxscoreacross/100.0                                               
            
            targetpoints = 1.0
            try:                        
                targetpoints = float(targetpointstmp) 
            except ValueError:
                targetpoints = 1.0
                
            if targetpoints > 0.0:                            
                score = score * targetpoints
            
            score = round(score,2)                      
            
            try:
                TPIUtils.submit_outcome(launch_data, problemNumber=problemNumber, problem_guid=problem_guid, score=score, duration=duration, submissionCount=2)                
            except Exception as e:                
                pass                           
                    
        return HttpResponse("Success",
                        status=200, content_type="application/json")      
    except Exception, e:
        response = HttpResponse('Error: postGradeQlSimIncorrectData:'  + str(e), 404)
        return response

#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_incorrect_data_count?plcholder=[qualsimsbusinessgoingglobalebert]
@csrf_exempt
@CorsHttpDecorator
def getQlSimIncorrectDataCount(request):    
    if not request.method == 'GET':
        return HttpResponse(status=400)   
         
    plcholder = request.GET.get('plcholder', 'knowdl')
    
    try:
        attempts = kQualsimAttempts.objects.filter(session_id__icontains=plcholder)
        siddict = kQualsimAttempts.objects.filter(session_id__icontains=plcholder).order_by().values_list('session_id',flat=True).distinct()
        
        package = {}
        package['plcholder'] = plcholder
        package['att_count'] = attempts.count() 
        package['sid_list'] = []
        
        for sid in siddict:                                
            package['sid_list'].append(sid)
            
        return HttpResponse(json.dumps(package),
                        status=200, content_type="application/json")      
        
    except Exception, e:
        response = HttpResponse('Error: getQlSimIncorrectData:'  + str(e), 404)
        return response    

#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_qlsim_duplicate_entries?status=complete&idxcnt=1000&sidx=0&orderby=-id
@csrf_exempt
@CorsHttpDecorator
def getQlSimDuplicateEntries(request):    
    if not request.method == 'GET':
        return HttpResponse(status=400)
        
    att_status = request.GET.get('status', 'complete')
    
    sidx = int(request.GET.get('sidx', 0))
    idxcnt = int(request.GET.get('idxcnt', 500))
    orderby = request.GET.get('orderby', '-id')
    eidx = sidx + idxcnt
    
    if att_status != 'inprogress': 
        att_status = 'complete'  
             
    try:        
        #attempts = kQualsimAttempts.objects.filter(status=att_status).order_by(orderby,'att_index')[sidx:eidx]
        attempts = kQualsimAttempts.objects.filter(status=att_status).order_by(orderby)[sidx:eidx]
        lcl_list = []        
        for attmpt in attempts:            
            lstatedata = json.loads(attmpt.state_data)  
            if lstatedata.get('Attempts'): 
                if lstatedata['Attempts'][0]['reqdData'].get('bookmarkData'):
                    gArrTracking = lstatedata['Attempts'][0]['reqdData']['bookmarkData']['gArrTracking']
                    hasDup = False
                    d_values = []  
                    userScore = 0.0  
                    maxScore = 0.0              
                    for trackobj in gArrTracking: 
                        d_value = trackobj['PgId']
                        if d_value not in d_values:
                            d_values.append(d_value)
                            try:
                                userScore += float(trackobj['OptScore'])
                            except ValueError:
                                userScore += 0.0
                            
                            try:
                                maxScore += float(trackobj['MaxScore'])
                            except ValueError:
                                maxScore += 0.0
                                                        
                        else:
                            hasDup = True                        
                    
                    if hasDup:
                        package = {}            
                        package['session_id'] = attmpt.session_id                            
                        package['att_index'] = attmpt.att_index 
                        package['status'] = attmpt.status
                        package['overallScore'] = 0
                        package['calculated_score'] = (userScore/maxScore)*100.0
                        attmaxscore = 0.0
                        try:
                            attmaxscore = float(lstatedata['Attempts'][0]['maxscore'])
                        except ValueError:
                            attmaxscore = -1.0
                            
                        package['attmaxscore'] = attmaxscore
                         
                        attmaxscoreacross = 0.0  
                        reses = kQualsimAttempts.objects.filter(status='complete', session_id = attmpt.session_id)
                        for res in reses:
                            lstatedataacross = json.loads(res.state_data)  
                            if attmaxscoreacross <=  float(lstatedataacross['Attempts'][0]['overallScore']):  
                                if(float(lstatedata['Attempts'][0]['overallScore']) != float(lstatedataacross['Attempts'][0]['overallScore'])): 
                                    attmaxscoreacross = float(lstatedataacross['Attempts'][0]['overallScore'])
                                                        
                        package['attmaxscoreacross'] = attmaxscoreacross               
                        package['overallScore'] = lstatedata['Attempts'][0]['overallScore']  
                        package['state']  = 'Done'
                        
                        lcl_list.append(package)
                    
        return HttpResponse(json.dumps(lcl_list),
                        status=200, content_type="application/json")      
    except Exception, e:
        response = HttpResponse('Error: getQlSimDuplicateEntries:'  + str(e), 404)
        return response

#http://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/update_qlsim_duplicate_entries?status=complete&idxcnt=1000&sidx=0&orderby=-id
@csrf_exempt
@CorsHttpDecorator
def updateQlSimDuplicateEntries(request):   
    resptextstring = 'begin:' 
    if not request.method == 'GET':
        return HttpResponse(status=400) 
    
    att_status = request.GET.get('status', 'all') 
     
    sidx = int(request.GET.get('sidx', 0))
    idxcnt = int(request.GET.get('idxcnt', 500)) 
    orderby = request.GET.get('orderby', '-id')
    eidx = sidx + idxcnt
     
    if att_status != 'inprogress': 
        att_status = 'complete'  
       
    try:        
        #attempts = kQualsimAttempts.objects.filter(status=att_status).order_by(orderby,'att_index')[sidx:eidx] 
        attempts = kQualsimAttempts.objects.filter(status=att_status).order_by(orderby)[sidx:eidx]          
        for attmpt in attempts:                                  
            lstatedata = json.loads(attmpt.state_data)  
            if lstatedata.get('Attempts'): 
                if lstatedata['Attempts'][0]['reqdData'].get('bookmarkData'):
                    gArrTracking = lstatedata['Attempts'][0]['reqdData']['bookmarkData']['gArrTracking']
                    hasDup = False
                    d_values = []
                    trimmed_array = []
                    userScore = 0.0  
                    maxScore = 0.0                 
                    for trackobj in gArrTracking: 
                        d_value = trackobj['PgId']
                        if d_value not in d_values:
                            d_values.append(d_value)
                            trimmed_array.append(trackobj)
                            try:
                                userScore += float(trackobj['OptScore'])
                            except ValueError:
                                userScore += 0.0                            
                            try:
                                maxScore += float(trackobj['MaxScore'])
                            except ValueError:
                                maxScore += 0.0
                        else:
                            hasDup = True                        
                    
                    if hasDup:
                        attmaxscore = -1.0
                        try:
                            attmaxscore = float(lstatedata['Attempts'][0]['maxscore'])
                        except ValueError:
                            attmaxscore = -1.0   
                        
                        attmaxscoreacross = 0.0  
                        reses = kQualsimAttempts.objects.filter(status='complete', session_id = attmpt.session_id)
                        for res in reses:
                            lstatedataacross = json.loads(res.state_data)  
                            if attmaxscoreacross <=  float(lstatedataacross['Attempts'][0]['overallScore']): 
                                if(float(lstatedata['Attempts'][0]['overallScore']) != float(lstatedataacross['Attempts'][0]['overallScore'])): 
                                    attmaxscoreacross = float(lstatedataacross['Attempts'][0]['overallScore'])                    
                        
                        if (attmaxscore <= attmaxscoreacross):                 
                            attmaxscore = attmaxscoreacross
                                         
                        caloverallscore = (userScore/maxScore)*100.0
                        if (attmaxscore <= caloverallscore):   
                            lstatedata['Attempts'][0]['maxscore'] = round(caloverallscore,2)
                            
                        lstatedata['Attempts'][0]['overallScore'] = round(caloverallscore,2)
                        lstatedata['Attempts'][0]['reqdData']['bookmarkData']['userScore'] = round(userScore,2)
                        lstatedata['Attempts'][0]['reqdData']['bookmarkData']['gArrTracking'] = trimmed_array
                        
                        attmpt.state_data = json.dumps(lstatedata)
                        attmpt.save()
                        
                        if (attmaxscore <= caloverallscore):  
                            session = SessionData.objects.get(session_id = attmpt.session_id)
                            launch_data = json.loads(session.launch_data)
                            duration = lstatedata['Attempts'][0]['duration']           
                            problemNumber = launch_data['custom_currentquestion']
                            problem_guid = launch_data['custom_target_' + launch_data['custom_currentquestion']] 
                            targetpointstmp = launch_data['custom_points_' + launch_data['custom_currentquestion']] 
                                                   
                            score = (userScore/maxScore)                                                
                            
                            targetpoints = 1.0
                            try:                        
                                targetpoints = float(targetpointstmp) 
                            except ValueError:
                                targetpoints = 1.0
                                
                            if targetpoints > 0.0:                            
                                score = score * targetpoints
                            
                            score = round(score,2)
                            try:
                                kresp = TPIUtils.submit_outcome(launch_data, problemNumber=problemNumber, problem_guid=problem_guid, score=score, duration=duration, submissionCount=2)
                                #kresp = "TPIUtils.submit_outcome()"
                                resptextstring = resptextstring + "submit_outcome Success: sessionid=" + attmpt.session_id + ", problemNumber=" + str(problemNumber) + ", problem_guid=" + str(problem_guid) + ", score= " + str(score) + ", duration=" + str(duration) + ", submissionCount=2, SuccessMsg:" + str(kresp)              
                            except Exception as e:
                                resptextstring = resptextstring + "submit_outcome failed: sessionid=" + attmpt.session_id + ", problemNumber=" + str(problemNumber) + ", problem_guid=" + str(problem_guid) + ", score= " + str(score) + ", duration=" + str(duration) + ", submissionCount=2, Exception:" + str(e)
                                                
        return HttpResponse(resptextstring,200)      
    except Exception, e:
        response = HttpResponse(resptextstring + '---------Error: updateQlSimDuplicateEntries:'  + str(e), 404)
        return response    
    

#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/import_csv/?tbl=&qlid=&flname=
@csrf_exempt
@CorsHttpDecorator
def importCsvData2(request):
    rspstr = "start"
    try:    
        dbtable = request.GET.get('tbl', "")
        qlid = request.GET.get('qlid',"naveenvinod")
        flname = request.GET.get('flname', "data")        
        flname = flname + ".txt"
        '''
        paramData = {}
        paramData['dbtable'] = dbtable
        paramData['qlid'] = qlid
        paramData['flname'] = flname
        
        return HttpResponse(json.dumps(paramData),
                        status=200, content_type="application/json")
        '''
        
        module_dir = os.path.dirname(__file__)  # get current directory
        file_path = os.path.join(module_dir, flname)
        lol = list(_csv.reader(open(file_path, 'rb'), delimiter='\t'))      
        
        failedlist = []
        mstAtteIdList = []
        errorList = []
        successList = []
                            
        if dbtable == 'assignmentdetails':
            kam.ql_assignmentdetails.objects.filter(QL_Id__icontains=qlid).delete()  
            for i in range(1,len(lol)): 
                try:
                    l_NumberOfAttempts = 0 
                    try:
                        l_NumberOfAttempts = int(lol[i][3])
                    except TypeError:
                        l_NumberOfAttempts = 0
                        
                    l_TargetPoints = 0 
                    try:
                        l_TargetPoints = float(lol[i][4])
                    except TypeError:
                        l_TargetPoints = 0
                    
                    l_Status = True
                    try:
                        l_Status = lol[i][8]
                        if l_Status == '0':
                            l_Status = False
                    except TypeError:
                        l_Status = True                        
                        
                    assgndetail = kam.ql_assignmentdetails.objects.create(                
                        Assignment_Id = lol[i][1], QL_Id = lol[i][2], QLTitle =lol[i][5], AssignmentTitle  = lol[i][7],
                        NumberOfAttempts = l_NumberOfAttempts, TargetPoints = l_TargetPoints, AssignmentLocation = lol[i][0],
                        Status =l_Status, UpdatedBy = 0, ObjectiveDetails =lol[i][10]
                    )
                    assgndetail.save()
                    successList.append(lol[i][0])
                except Exception as ine:
                    failedlist.append(lol[i][0])
                    errorList.append(str(ine))
                    
        if dbtable == 'masterquestions':
            kam.ql_masterquestions.objects.filter(QL_Id__icontains=qlid).delete()  
            for i in range(1,len(lol)): 
                try:                        
                    l_TotalPoints = 0 
                    try:
                        l_TotalPoints = Decimal(lol[i][6])
                    except TypeError:
                        l_TotalPoints = 0
                        
                    mastques = kam.ql_masterquestions.objects.create(                        
                        QL_Id = lol[i][1], PageId = lol[i][2], QuestionId = lol[i][3], QuestionText = str(lol[i][4]),
                        Options = str(lol[i][5]), TotalPoints = l_TotalPoints, QuestionTitle =lol[i][7],
                        AdditionalInfo = lol[i][8], Type = lol[i][9]
                    )
                    mastques.save()
                    successList.append(lol[i][0])
                except Exception as ine:
                    failedlist.append(lol[i][0])
                    errorList.append(str(lol[i][0]) + "------" + str(ine))
        
        if dbtable == 'masterattempts':            
            #ids = kam.ql_masterattempts.objects.filter(QL_Id__icontains=qlid).values_list('Id', flat=True)
            #kam.ql_questionattemptdetails.objects.filter(Id__in=ids).delete()  
            #kam.ql_masterattempts.objects.filter(QL_Id__icontains=qlid).delete()            
            for i in range(1,len(lol)):   
                try:         
                    l_TimeSpent = 0 
                    try:
                        l_TimeSpent = Decimal(lol[i][10])
                    except TypeError:
                        l_TimeSpent = 0 
                        
                    l_Score = 0 
                    try:
                        l_Score = Decimal(lol[i][11])
                    except TypeError:
                        l_Score = 0
                    
                    l_Points = 0 
                    try:
                        l_Points = Decimal(lol[i][12])
                    except TypeError:
                        l_Points = 0 
                    
                    mstatte = kam.ql_masterattempts.objects.create(
                        Student_Id = lol[i][1],Assignment_Id = lol[i][2], QL_Id = lol[i][3].encode("utf-8"),
                        StudentName = lol[i][4], AssignmentTitle = lol[i][5], Role = lol[i][6],
                        StartDate = datetime.datetime.strptime(lol[i][7], '%Y-%m-%d %H:%M:%S.%f'),
                        EndDate = datetime.datetime.strptime(lol[i][8], '%Y-%m-%d %H:%M:%S.%f'),
                        CompletionStatus = lol[i][9], TimeSpent =l_TimeSpent, Score = l_Score, Points =l_Points,
                        AssignmentLocation = lol[i][0],Session_Id = lol[i][14], ReportStatus = lol[i][15]
                    )                     
                    mstatte.save()
                    successList.append(lol[i][0])
                                        
                except Exception as ine:
                    failedlist.append(lol[i][0])
                    errorList.append(str(ine))
                    
        if dbtable == 'questionattemptdetails1122':               
            #ids = kam.ql_masterattempts.objects.filter(QL_Id__icontains=qlid).values_list('Id', flat=True)
            #kam.ql_questionattemptdetails.objects.filter(Id__in=ids).delete()    
            for i in range(1,len(lol)):   
                try:                    
                    l_Score = 0 
                    try:
                        l_Score = Decimal(lol[i][6])
                    except TypeError:
                        l_Score = 0
                    
                    l_Points = 0 
                    try:
                        l_Points = Decimal(lol[i][7])
                    except TypeError:
                        l_Points = 0 
                                
                    l_TimeSpent = 0 
                    try:
                        l_TimeSpent = Decimal(lol[i][8])
                    except TypeError:
                        l_TimeSpent = 0                    
                    
                    l_MstAttemptId = '-1'
                    try:
                        l_MstAttemptId = lol[i][1]
                    except TypeError:
                        l_MstAttemptId = '-1' 
                        
                    l_AdditionalInfo = ''
                    try:
                        l_AdditionalInfo = lol[i][9]
                        if l_AdditionalInfo == 'NULL':
                            l_AdditionalInfo = ''
                    except TypeError:
                        l_AdditionalInfo = '' 
                    
                    db_MstAttempt = kam.ql_masterattempts.objects.get(AssignmentLocation = l_MstAttemptId)                                      
                    
                    mstatte = kam.ql_questionattemptdetails.objects.create(                        
                        MstAttemptId = db_MstAttempt.Id, PageId = lol[i][2], QuestionId = lol[i][3],  SelOptionId = lol[i][4],
                        CorrectStatus = lol[i][5], Score = l_Score, Points = l_Points, TimeSpent = l_TimeSpent,
                        AdditionalInfo = l_AdditionalInfo
                    )                     
                    mstatte.save()
                    successList.append(lol[i][0])
                    
                except Exception as ine:
                    failedlist.append(lol[i][0]) 
                    mstAtteIdList.append(lol[i][1]) 
                    errorList.append(str(ine))
                      
                                
        StatusData = {}
        StatusData['TableName1122'] = dbtable
        StatusData['SuccessList'] = successList
        StatusData['FailedList'] = failedlist
        StatusData['ErrorList'] = errorList
        StatusData['QAD_FailedMstIdList'] = mstAtteIdList
        
        
        return HttpResponse(json.dumps(StatusData),
                        status=200, content_type="application/json")
        
    except Exception as e:
        rspstr += ", TestError:" + str(e)
        return HttpResponse(rspstr,200)   
 

#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/import_csv/?tbl=&qlid=&flname=
@csrf_exempt
@CorsHttpDecorator
def importCsvData4(request):
    rspstr = "start"
    try:    
        dbtable = request.GET.get('tbl', "")
        qlid = request.GET.get('qlid',"naveenvinod")
        flname = request.GET.get('flname', "data")        
        flname = flname + ".txt"
        '''
        paramData = {}
        paramData['dbtable'] = dbtable
        paramData['qlid'] = qlid
        paramData['flname'] = flname
        
        return HttpResponse(json.dumps(paramData),
                        status=200, content_type="application/json")
        '''
        
        module_dir = os.path.dirname(__file__)  # get current directory
        file_path = os.path.join(module_dir, flname)
        lol = list(_csv.reader(open(file_path, 'rb'), delimiter='\t'))      
        
        failedlist = []
        mstAtteIdList = []
        errorList = []
        successList = []
                            
        if dbtable == 'assignmentdetails':
            kam.ql_assignmentdetails.objects.filter(QL_Id__icontains=qlid).delete()  
            for i in range(1,len(lol)): 
                try:
                    l_NumberOfAttempts = 0 
                    try:
                        l_NumberOfAttempts = int(lol[i][3])
                    except TypeError:
                        l_NumberOfAttempts = 0
                        
                    l_TargetPoints = 0 
                    try:
                        l_TargetPoints = float(lol[i][4])
                    except TypeError:
                        l_TargetPoints = 0
                    
                    l_Status = True
                    try:
                        l_Status = lol[i][8]
                        if l_Status == '0':
                            l_Status = False
                    except TypeError:
                        l_Status = True                        
                        
                    assgndetail = kam.ql_assignmentdetails.objects.create(                
                        Assignment_Id = lol[i][1], QL_Id = lol[i][2], QLTitle =lol[i][5], AssignmentTitle  = lol[i][7],
                        NumberOfAttempts = l_NumberOfAttempts, TargetPoints = l_TargetPoints, AssignmentLocation = lol[i][0],
                        Status =l_Status, UpdatedBy = 0, ObjectiveDetails =lol[i][10]
                    )
                    assgndetail.save()
                    successList.append(lol[i][0])
                except Exception as ine:
                    failedlist.append(lol[i][0])
                    errorList.append(str(ine))
                    
        if dbtable == 'masterquestions':
            kam.ql_masterquestions.objects.filter(QL_Id__icontains=qlid).delete()  
            for i in range(1,len(lol)): 
                try:                        
                    l_TotalPoints = 0 
                    try:
                        l_TotalPoints = Decimal(lol[i][6])
                    except TypeError:
                        l_TotalPoints = 0
                        
                    mastques = kam.ql_masterquestions.objects.create(                        
                        QL_Id = lol[i][1], PageId = lol[i][2], QuestionId = lol[i][3], QuestionText = str(lol[i][4]),
                        Options = str(lol[i][5]), TotalPoints = l_TotalPoints, QuestionTitle =lol[i][7],
                        AdditionalInfo = lol[i][8], Type = lol[i][9]
                    )
                    mastques.save()
                    successList.append(lol[i][0])
                except Exception as ine:
                    failedlist.append(lol[i][0])
                    errorList.append(str(lol[i][0]) + "------" + str(ine))
        
        if dbtable == 'masterattempts':            
            #ids = kam.ql_masterattempts.objects.filter(QL_Id__icontains=qlid).values_list('Id', flat=True)
            #kam.ql_questionattemptdetails.objects.filter(Id__in=ids).delete()  
            #kam.ql_masterattempts.objects.filter(QL_Id__icontains=qlid).delete()            
            for i in range(1,len(lol)):   
                try:         
                    l_TimeSpent = 0 
                    try:
                        l_TimeSpent = Decimal(lol[i][10])
                    except TypeError:
                        l_TimeSpent = 0 
                        
                    l_Score = 0 
                    try:
                        l_Score = Decimal(lol[i][11])
                    except TypeError:
                        l_Score = 0
                    
                    l_Points = 0 
                    try:
                        l_Points = Decimal(lol[i][12])
                    except TypeError:
                        l_Points = 0 
                    
                    mstatte = kam.ql_masterattempts.objects.create(
                        Student_Id = lol[i][1],Assignment_Id = lol[i][2], QL_Id = lol[i][3],
                        StudentName = lol[i][4], AssignmentTitle = lol[i][5], Role = lol[i][6],
                        StartDate = datetime.datetime.strptime(lol[i][7], '%Y-%m-%d %H:%M:%S.%f'),
                        EndDate = datetime.datetime.strptime(lol[i][8], '%Y-%m-%d %H:%M:%S.%f'),
                        CompletionStatus = lol[i][9], TimeSpent =l_TimeSpent, Score = l_Score, Points =l_Points,
                        AssignmentLocation = lol[i][0],Session_Id = lol[i][14], ReportStatus = lol[i][15]
                    )                     
                    mstatte.save()
                    successList.append(lol[i][0])
                                        
                except Exception as ine:
                    failedlist.append(lol[i][0])
                    errorList.append(str(ine))
                    
        if dbtable == 'questionattemptdetails1122':               
            #ids = kam.ql_masterattempts.objects.filter(QL_Id__icontains=qlid).values_list('Id', flat=True)
            #kam.ql_questionattemptdetails.objects.filter(Id__in=ids).delete() 
            try:
                knowdlAttIdLocations = kam.ql_masterattempts.objects.values("Id","AssignmentLocation").all()
                DictOfMasterAttmptIDLocation = {}
                if knowdlAttIdLocations.count() > 0 :    
                    for kid in knowdlAttIdLocations :
                        DictOfMasterAttmptIDLocation[kid["AssignmentLocation"]] = kid["Id"]
            except Exception as exc:
                errorList.append(str(exc))                 
            for i in range(1,len(lol)):   
                try:                    
                    l_Score = 0 
                    try:
                        l_Score = Decimal(lol[i][6])
                    except TypeError:
                        l_Score = 0
                    
                    l_Points = 0 
                    try:
                        l_Points = Decimal(lol[i][7])
                    except TypeError:
                        l_Points = 0 
                                
                    l_TimeSpent = 0 
                    try:
                        l_TimeSpent = Decimal(lol[i][8])
                    except TypeError:
                        l_TimeSpent = 0                    
                    
                    l_MstAttemptId = '-1'
                    try:
                        l_MstAttemptId = lol[i][1]
                    except TypeError:
                        l_MstAttemptId = '-1' 
                        
                    l_AdditionalInfo = ''
                    try:
                        l_AdditionalInfo = lol[i][9]
                        if l_AdditionalInfo == 'NULL':
                            l_AdditionalInfo = ''
                    except TypeError:
                        l_AdditionalInfo = '' 
                    
                    #db_MstAttemptidList = kam.ql_masterattempts.objects.filter(AssignmentLocation = l_MstAttemptId).values("Id").all()
                                                                             
                    
                    mstatte = kam.ql_questionattemptdetails.objects.create(                        
                        MstAttemptId = int(DictOfMasterAttmptIDLocation[l_MstAttemptId]), PageId = lol[i][2], QuestionId = lol[i][3],  SelOptionId = lol[i][4],
                        CorrectStatus = lol[i][5], Score = l_Score, Points = l_Points, TimeSpent = l_TimeSpent,
                        AdditionalInfo = l_AdditionalInfo
                    )                     
                    mstatte.save()
                    successList.append(lol[i][0])
                    
                except Exception as ine:
                    failedlist.append(lol[i][0]) 
                    mstAtteIdList.append(lol[i][1]) 
                    errorList.append(str(ine))
                      
                                
        StatusData = {}
        StatusData['TableName1122'] = dbtable
        StatusData['SuccessList'] = successList
        StatusData['FailedList'] = failedlist
        StatusData['ErrorList'] = errorList
        StatusData['QAD_FailedMstIdList'] = mstAtteIdList
        
        
        return HttpResponse(json.dumps(StatusData),
                        status=200, content_type="application/json")
        
    except Exception as e:
        rspstr += ", TestError:" + str(e)
        return HttpResponse(rspstr,200)   
    
   

#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/update_ques_att_data/?ql_id=[qlid]
@csrf_exempt
@CorsHttpDecorator
def updateQuesAttemptDetails(request):
    retstr ="Start"
    asgnLoc = []
    try:
        qlidlike = request.GET.get('ql_id', "naveentestid_no_id")
        knowdlAttIds = kam.ql_masterattempts.objects.filter(QL_Id__icontains=qlidlike).values("Id","AssignmentLocation").all()
        retstr = str(knowdlAttIds.count())
        if knowdlAttIds.count() > 0 :    
            for kid in knowdlAttIds :
                try:
                    mstidqad = int(kid["AssignmentLocation"])
                    econAttId = kid["Id"]
                    updatecount = kam.ql_questionattemptdetails.objects.filter(MstAttemptId=mstidqad).update(MstAttemptId=econAttId)
                    retstr = retstr + "----UpdateCount:" + str(updatecount)
                except Exception as exc:
                    asgnLoc.append("InnerExcep: AsgnLoc-" + kid["AssignmentLocation"] + "Error-" + str(exc)) 
    
    except Exception as e:
        retstr = retstr + "Main Exception" + str(e)
        
    TraceData = {}  
    TraceData['StackTrace'] = retstr      
    TraceData['FailedAsgLocList'] = asgnLoc 
     
    return HttpResponse(json.dumps(TraceData),
                        status=200, content_type="application/json")
    

#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_update_ques_att_data/?ql_id=[qlid]
@csrf_exempt
@CorsHttpDecorator
def getupdateQuesAttemptDetails(request):
    retstr ="Start"
    asgnLoc = []
    try:
        qlidlike = request.GET.get('ql_id', "naveentestid_no_id")
        knowdlAttIds = kam.ql_masterattempts.objects.filter(QL_Id__icontains=qlidlike).values("Id","AssignmentLocation").all()
        retstr = str(knowdlAttIds.count())
        if knowdlAttIds.count() > 0 :    
            for kid in knowdlAttIds :
                try:
                    mstidqad = int(kid["AssignmentLocation"])
                    econAttId = kid["Id"]
                    updatecount = kam.ql_questionattemptdetails.objects.filter(MstAttemptId=mstidqad).count()
                    retstr = retstr + "----UpdateCount:" + str(updatecount)
                except Exception as exc:
                    asgnLoc.append("InnerExcep: AsgnLoc-" + kid["AssignmentLocation"] + "Error-" + str(exc)) 
    
    except Exception as e:
        retstr = retstr + "Main Exception" + str(e)
        
    TraceData = {}
    TraceData['StackTrace'] = retstr      
    TraceData['FailedAsgLocList'] = asgnLoc 
     
    return HttpResponse(json.dumps(TraceData),
                        status=200, content_type="application/json")
          

#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_table_count/?tbl=assignmentdetails
@csrf_exempt
@CorsHttpDecorator
def gettableCount(request):
    dbtable = request.GET.get('tbl', "")
    #kam.ql_assignmentdetails.objects.all().delete()
    #kam.ql_masterquestions.objects.all().delete()
    #kam.ql_masterattempts.objects.all().delete()
    #kam.ql_questionattemptdetails.objects.all().delete()
    
    template_mappings = {} 
    strtrace = "Start555"   
    try:       
        strtrace = strtrace + request.META.get("HTTP_HOST")
        r = requests.get("https://" + request.META.get("HTTP_HOST") + '/knowdl_revel_sim/commonfiles/template_mappings.json')
        if r.status_code == 200:
            template_mappings = r.json()
            strtrace = strtrace + " ----Key-value:" + template_mappings["JWKS_URL"] + " ----temp:" + template_mappings["38a1192c-778f-11e7-b5a5-be2e44b06b34"]
        else: 
            strtrace = strtrace + r.url   
            
    except Exception as jsonexc:
        strtrace = strtrace + str(jsonexc) 
        #return redirect('/knowdl_revel_sim/commonfiles/template_mappings.json')
        
        
    return HttpResponse(strtrace,200)         
            
    
    if dbtable == 'assignmentdetails':        
        rcount = kam.ql_assignmentdetails.objects.count()
        return HttpResponse(rcount,200)  
    
    if dbtable == 'masterquestions':
        rcount = kam.ql_masterquestions.objects.count()
        return HttpResponse(rcount,200)  
    
    if dbtable == 'masterattempts':
        rcount = kam.ql_masterattempts.objects.count()
        return HttpResponse(rcount,200)   
    
    if dbtable == 'questionattemptdetails':
        rcount = kam.ql_questionattemptdetails.objects.count()
        return HttpResponse(rcount,200) 
    
    return HttpResponse("success",200)     
    
#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_table_count/?tbl=assignmentdetails

@csrf_exempt
@CorsHttpDecorator
def deletetableData(request):
    dbtable = request.GET.get('tbl', "")
    
    if dbtable == 'assignmentdetails':        
        kam.ql_assignmentdetails.objects.all().delete()
    
    if dbtable == 'masterquestions':
        kam.ql_masterquestions.objects.all().delete()
    
    if dbtable == 'masterattempts':
        kam.ql_masterattempts.objects.all().delete()
    
    if dbtable == 'questionattemptdetails':
        kam.ql_questionattemptdetails.objects.all().delete()
    
    return HttpResponse("success",200)  


#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_dup_attempt_data/
@csrf_exempt
@CorsHttpDecorator
def getDuplicateMAttempts(request):    
    kndllist = ["Student1 Knowdl", "Student2 Knowdl", "Idelle K3 Ingenito", "Shelly K10 Saner", "Kermit K4 Kelly", "Loretta K5 Leight", "Nora K6 Newberg", "Pei K7 Pasquariello", "Pinkie K8 Pharr", "Patty K9 Prince"]
    begin_date = datetime.date(2017, 11, 5)    
    studnameslist = list(kam.ql_masterattempts.objects.filter(StartDate__gt = datetime.datetime.combine(begin_date, datetime.time.max), CompletionStatus = 'complete').exclude(StudentName__in = kndllist).values("StudentName", "StartDate").all())   
    
    
    for stu in studnameslist:
        stu["StartDate"] = (stu["StartDate"]).strftime("%Y-%m-%d %H:%M:%S")
        
    retobj = {}
    retobj["TraceValue"] = "111"
    retobj["StudentList"] = studnameslist
    
        
    return HttpResponse(json.dumps(retobj),
                        status=200, content_type="application/json")

    


#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/update_dup_attempt_data/?dupids=''&action=donothing
@csrf_exempt
@CorsHttpDecorator
def updateDuplicateMAttempts(request):
    dupids = request.GET.get('dupids', "")
    action = request.GET.get('action', "none")
    failedlist = [] 
    retstr = ""  
    try:
        dupidslist = dupids.split(",")
        if dupidslist.count()>0:
            for dupr in dupidslist:
                if action == "delete":  
                    try:
                        kam.ql_masterattempts.objects.filter(Id=int(dupr)).delete()
                    except Exception as inn: 
                        failedlist.append(dupr + str(inn)) 
                else:
                    failedlist.append(int(dupr))   
            
    except Exception as e:
        retstr = retstr + "Main Exception" + str(e)
        
    TraceData = {}  
    TraceData['failedlist'] = failedlist      
    TraceData['mainExce'] = retstr 
     
    return HttpResponse(json.dumps(TraceData),
                        status=200, content_type="application/json") 
    

#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_asgn_data/ 
@csrf_exempt
@CorsHttpDecorator
def GetAssignmentData(request):
    tracestr = "Start GetAssignmentData:"
    yval = int(request.GET.get('y', "2017"))
    mval = int(request.GET.get('m', "11"))
    dval = int(request.GET.get('d', "5"))    
    qlidlist = []
    assignidList = []
    AttemptArray = []
    assignList = []
    try:
        begin_date = datetime.date(yval, mval, dval)     
        tracestr = tracestr + "BeginDate:" + datetime.datetime.combine(begin_date, datetime.time.max).strftime("%Y-%m-%d %H:%M:%S")
        valueslist = kam.ql_masterattempts.objects.filter(StartDate__gt = datetime.datetime.combine(begin_date, datetime.time.max)).values("QL_Id", "Assignment_Id").all()
        
        tracestr = tracestr + "valueslist.count()" + str(valueslist.count())
        if valueslist.count()>0:
            for lval in valueslist:
                assignidList.append(lval["Assignment_Id"])
                qlidlist.append(lval["QL_Id"])         
        
        
        
        tracestr = tracestr + "Fetching Assignment List-->"
        assignments = kam.ql_assignmentdetails.objects.filter(Assignment_Id__in = assignidList , QL_Id__in = qlidlist).all()
        for asgn in assignments:
            try:  
                asgnobj = {}
                asgnobj["Id"] = asgn.Id
                asgnobj["Assignment_Id"] = asgn.Assignment_Id
                asgnobj["QL_Id"] = asgn.QL_Id
                asgnobj["QLTitle"] = asgn.QLTitle
                asgnobj["AssignmentTitle"]  = asgn.AssignmentTitle
                asgnobj["NumberOfAttempts"] = asgn.NumberOfAttempts
                asgnobj["TargetPoints"] = asgn.TargetPoints
                asgnobj["AssignmentLocation"] = asgn.AssignmentLocation
                asgnobj["Status"] = asgn.Status
                asgnobj["UpdatedBy"] = asgn.UpdatedBy
                asgnobj["ObjectiveDetails"] = asgn.ObjectiveDetails
                
                assignList.append(asgnobj)
            except Exception as innerex2:
                    tracestr = tracestr + "Error In Parsing Assignment Data: Assignment_Id" + asgn.Assignment_Id + "-Exception:" + str(innerex2)
                        
            
        tracestr = tracestr + "Completed Fetching Assignment List-->"    
        tracestr = tracestr + "Fetching Attempts List-->"
        attempts = kam.ql_masterattempts.objects.filter(StartDate__gt = datetime.datetime.combine(begin_date, datetime.time.max)).all()
        tracestr = tracestr + "Completed Fetching Attempt List-->"        
        
        for att in attempts:
            attobj = {}        
            try:        
                attobj["Id"] = att.Id
                attobj["Student_Id"] = att.Student_Id
                attobj["Assignment_Id"] = att.Assignment_Id
                attobj["QL_Id"] = att.QL_Id
                attobj["StudentName"] =att.StudentName
                attobj["AssignmentTitle"] = att.AssignmentTitle
                attobj["Role"] =att.Role
                attobj["StartDate"] = att.StartDate.strftime("%Y-%m-%d %H:%M:%S")
                attobj["EndDate"] = att.EndDate.strftime("%Y-%m-%d %H:%M:%S")
                attobj["CompletionStatus"] = att.CompletionStatus
                attobj["TimeSpent"] = str(att.TimeSpent)
                attobj["Score"] = str(att.Score)
                attobj["Points"] = str(att.Points)
                attobj["AssignmentLocation"] = att.AssignmentLocation
                attobj["Session_Id"] = att.Session_Id
                attobj["ReportStatus"] = att.ReportStatus           
                try:
                    detArr = []
                    attdetails = kam.ql_questionattemptdetails.objects.filter(MstAttemptId = att.Id).all()  
                    for attdet in attdetails:
                        detobj = {} 
                        detobj["Id"] = attdet.Id 
                        detobj["MstAttemptId"] = attdet.MstAttemptId
                        detobj["PageId"] = attdet.PageId
                        detobj["QuestionId"] = attdet.QuestionId
                        detobj["SelOptionId"] = attdet.SelOptionId
                        detobj["CorrectStatus"] = attdet.CorrectStatus
                        detobj["Score"] = str(attdet.Score)
                        detobj["Points"] = str(attdet.Points)
                        detobj["TimeSpent"] = str(attdet.TimeSpent)
                        detobj["AdditionalInfo"] = attdet.AdditionalInfo
                        detArr.append(detobj)                        
                         
                    attobj["QuestionAttemptDetails"] = detArr
                except Exception as innerex1:
                    tracestr = tracestr + "Error In Fetching Question Details: MstAttemptId=" + str(att.Id) + "Exception:" + str(innerex1)            
            except Exception as innerex:
                tracestr = tracestr + "Error In Parsing Attempt: AttemptId" + str(att.Id) + "-Exception:" + str(innerex)
                    
            AttemptArray.append(attobj)
        
        tracestr = "Trace Complete."
    except Exception as mainEx:
        tracestr = tracestr + "Main Exception:" + str(mainEx)
    
    retJson = {}
    retJson["TraceData"] = tracestr
    retJson["AssignmentData"] = assignList
    retJson["Attempts"] = AttemptArray
    
    
    return HttpResponse(json.dumps(retJson),
                        status=200, content_type="application/json")


@csrf_exempt
@CorsHttpDecorator
# https://pe-xl-dev.knowdl.com/econservice/data/econ/common_services/export_assign_json/
def exportAssignJSON(request):
    AssignmentData = {}
    AsgnArray = []
    localDict = {}
    try:
        begin_date = datetime.date(2018, 2, 1)
        # select count(*)  from gldata_sessiondata where session_launch_date > '2018-02-01'
        # and session_id like '%_qualsimsmarketingpricingstrategies%' order by
        # session_launch_date
        sessions = SessionData.objects.filter(
            session_launch_date__gt=datetime.datetime.combine(
                begin_date, datetime.time.max), session_id__contains='_qualsimsmarketingpricingstrategies').order_by('session_launch_date')

        totalSessions = 0
        for s in sessions:
            totalSessions = totalSessions + 1
            launchdata = json.loads(s.launch_data)
            QL_Id = launchdata['custom_target_' +
                               launchdata['custom_currentquestion']]
            AssignmentId = launchdata['custom_resource_id']

            if localDict.get(QL_Id + AssignmentId) == None:
                localDict[QL_Id + AssignmentId] = 1
                sObj = {}
                sObj["QL_Id"] = QL_Id
                sObj["QLTitle"] = launchdata['custom_questiontitle_' +
                                             launchdata['custom_currentquestion']]
                sObj["Assignment_Id"] = AssignmentId
                sObj["AssignmentLocation"] = 'pe-xl-prod.knowdl.com'
                sObj["AssignmentTitle"] = launchdata['custom_assignmenttitle']
                sObj["NumberOfAttempts"] = launchdata['custom_attemptsallowed']
                sObj["TargetPoints"] = launchdata['custom_points_' +
                                                  launchdata['custom_currentquestion']]

                AsgnArray.append(sObj)

        AssignmentData['totalSessions'] = totalSessions
        AssignmentData['newSessions'] = AsgnArray

    except Exception as e:
        AssignmentData["mainerror"] = str(e)

    return HttpResponse(json.dumps(AssignmentData),
                        status=200, content_type="application/json")




@csrf_exempt
@CorsHttpDecorator
# https://pe-xl-dev.knowdl.com/econservice/data/econ/common_services/export_attempt_json/
def exportAttemptJSON(request):
    nmData = {}
    failedQIds = []
    failedAttIds = []
    failedSids = []
    UserSessions = []
    nmerrors = []
    try:
        begin_date = datetime.date(2018, 2, 1)
        # select count(*) from common_services_kqualsimattempts where session_id in
        #(select session_id from gldata_sessiondata where session_launch_date > '2018-02-01'
        # and session_id like '%_qualsimsmarketingpricingstrategies%' order by
        # session_launch_date )

        sid_dict = SessionData.objects.filter(
            session_launch_date__gt=datetime.datetime.combine(
                begin_date, datetime.time.max), session_id__contains='_qualsimsmarketingpricingstrategies').exclude(problem_state_data='lostattempts').order_by('session_launch_date').values_list('session_id', flat=True).distinct()[:1000]

        nmData['sid_dict_count'] = sid_dict.count()

        for sid in sid_dict:
            try:
                UserSession = {}
                UserSession['SessionId'] = sid

                session = SessionData.objects.get(session_id=sid)
                attempts = kQualsimAttempts.objects.filter(
                    session_id=sid).order_by('att_index')

                UserSession['Attempts'] = []

                for att in attempts:
                    try:
                        attJson = {}
                        launchdata = json.loads(session.launch_data)

                        attJson['QL_Id'] = launchdata['custom_target_' +
                                                      launchdata['custom_currentquestion']]
                        attJson['Assignment_Id'] = launchdata['custom_resource_id']
                        attJson['Student_Id'] = launchdata['user_id']
                        attJson['StudentName'] = launchdata["custom_firstname"] + \
                            " " + launchdata["custom_lastname"]
                        attJson['AssignmentTitle'] = launchdata['custom_assignmenttitle']
                        attJson['AssignmentLocation'] = 'pe-xl-prod.knowdl.com'
                        attJson['Role'] = launchdata['roles']

                        attJson['StartDate'] = datetime.datetime.strftime(
                            att.start_date, '%Y-%m-%d %H:%M:%S.%f')
                        attJson['EndDate'] = datetime.datetime.strftime(
                            att.end_date, '%Y-%m-%d %H:%M:%S.%f')

                        stateData = json.loads(att.state_data)

                        attJson['CompletionStatus'] = stateData['Attempts'][0]['status']
                        attJson['TimeSpent'] = stateData['Attempts'][0]['duration']
                        attJson['Score'] = stateData['Attempts'][0]['overallScore']
                        attJson['Points'] = stateData['Attempts'][0]['reqdData']['bookmarkData']['userScore']
                        attJson['Session_Id'] = sid
                        attJson['ReportStatus'] = 'inactive'
                        attJson['att_index'] = att.att_index

                        attJson['Questions'] = []

                        ques = stateData['Attempts'][0]['reqdData']['bookmarkData']['gArrTracking']

                        for q in ques:
                            try:
                                qjson = {}
                                qjson['PageId'] = q['PgId']
                                qjson['QuestionId'] = q['PgId']
                                qjson['SelOptionId'] = q['OptId']
                                qjson['CorrectStatus'] = ''
                                qjson['Score'] = float(
                                    q['OptScore']) / float(q['MaxScore']) * 100.00
                                qjson['Points'] = q['OptScore']
                                qjson['TimeSpent'] = 20
                                qjson['AdditionalInfo'] = ''

                                attJson['Questions'].append(qjson)
                            except Exception as ex1:
                                failedQIds.append(q['PgId'])
                                nmerrors.append(str(ex1))
                                pass

                        UserSession['Attempts'].append(attJson)

                    except Exception as ex2:
                        failedAttIds.append(str(ex2))
                        nmerrors.append(str(ex2))
                        pass

                UserSessions.append(UserSession)
            except Exception as ex3:
                failedSids.append(sid)
                nmerrors.append(str(ex3))
                pass

            session.problem_state_data = 'lostattempts'
            session.save()

        nmData['UserSessions'] = UserSessions
        nmData['FailedSids'] = failedSids
        nmData['FailedAttIds'] = failedAttIds
        nmData['FailedQid'] = failedQIds
        nmData['Errors'] = nmerrors

    except Exception as e:
        nmData['mainError'] = str(e)

    return HttpResponse(json.dumps(nmData),
                        status=200, content_type="application/json")





#end of file








