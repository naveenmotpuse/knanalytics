
from django.http import HttpResponse, HttpResponseRedirect
from models import *
from knanalytics import TPIUtils
from django.views.decorators.csrf import csrf_exempt
import  json
from xlsims.sims_table import *
from gllaunch.models import TPI_Launch_Log
from django.utils import timezone
from django.conf import settings
import requests
import uuid
import datetime
from django.db import transaction
from django.db.models import Count


@csrf_exempt
def manualgradepostreport(request):
    dstring = "<table><tr><td>User Id</td><td>Resource Id</td><td>Target App</td><td>Score</td><td>Start Date</td><td>End Date</td></tr>"
    sobjects = SimsSession.objects.filter(manualupdatefor = 'topscore', topScore = True).order_by('id').values_list('iSession__user_id','iSession__resource_id' ,'iSession__target_app', 'score','start', 'end')[0:10000]
    for item in sobjects:
	try:
	    dstring  = dstring + "<tr><td>" + item[0] + "</td><td> " + item[1] + "</td><td>" + item[2] +  "</td><td>" + str(item[3]) +  "</td><td>" + TPIUtils.timestampstr(item[4]) + "</td><td>" + TPIUtils.timestampstr(item[5]) + "</td></tr>" 	
	except Exception, e:
	    dstring = dstring + "<tr><td>" + str(e) + "</td><tr>"

    dstring = dstring + "</table>"

    return HttpResponse(dstring, status=200)
    

@csrf_exempt
def postatmsimgrades(request):    
    data = []    
    try:    
	#sobjects = SimsSession.objects.filter(iSession__user_id = 'urn:udson:pearson.com/xl/highered:user/29782202', score__gt = 0, active=False).values_list('iSession__id').distinct()[:3000]
        sobjects = SimsSession.objects.filter(score__gt = 0, active=False, manualupdatefor='topscore', topScore=True).exclude(manualupdatefor = 'completiondateissue').values_list('iSession__id').distinct()[:3000]
        for item in sobjects:
            udata = {}
            udata['iSession__id'] = item[0]                      
            simSessions = SimsSession.objects.filter(iSession__id=item[0], active=False).order_by('-score')
            score = 0 
            duration = 0  
            attempts = len(simSessions)             
	    #c_date = timezone.now()
            if len(simSessions)>0:
                udata['usertopscore'] = simSessions[0].score  
                udata['userminscore'] = simSessions[attempts-1].score
                
                for r in simSessions:
                    try:
                        duration += int((r.end - r.start).seconds)		
                    except Exception, e:
                        duration = duration
                    r.topScore = False
		    r.manualupdatefor = 'completiondateissue'
                    r.save()                    
                                         
                score = simSessions[0].score                      
		c_date = simSessions[0].end          
                simSessions[0].topScore = True         
		simSessions[0].manualupdatefor = 'completiondateissue'   
                simSessions[0].save()
                
                udata['duration'] = duration  
                udata['score'] = score 
                udata['attempts'] = attempts
		udata['enddate'] = TPIUtils.timestampstr(c_date) 
                #udata['LaunchParam'] = simSessions[0].iSession.getLaunchParam()    
                #data.append(udata) 
		try:
                    sendTPIReportBackDate(score, duration, attempts, simSessions[0].iSession.getLaunchParam(),c_date)          
		except Exception, inne:
		    udata['error'] = str(inne)

                data.append(udata)                       
        
        return HttpResponse(json.dumps(data), status=200)
    except Exception, e:
        return HttpResponse("Error:" + str(e), status=401)


@csrf_exempt
def getDupSimSessions1(request):    
    data = []
    try:    
        sobjects = SimsSession.objects.values('iSession__user_id','iSession__resource_id','iSession__target_app').filter(topScore=True).values_list('iSession__user_id', 'iSession__resource_id', 'iSession__target_app')
        for item in sobjects:
            udata = {}
            udata['user_id'] = item[0]
            udata['resource_id'] = item[1]
            udata['target_app'] = item[2]
            simSessions = SimsSession.objects.filter(iSession__user_id=item[0], iSession__resource_id=item[1], iSession__target_app=item[2]).order_by('-score')
            if simSessions[0].topScore == False:
                actualTopScore = simSessions[0].score
                fsims = simSessions.filter(topScore = True).all()
		score = []
		for nav in fsims:
		    score.append(nav.score)

                udata['actualTopScore'] = actualTopScore
                udata['score'] = score                             
		data.append(udata)
            #else:
                #udata['score'] = simSessions[0].score 
                #udata['isCorrect'] = True 
                
            #data.append(udata)
        
        return HttpResponse(json.dumps(data), status=200)
    except Exception, e:
        return HttpResponse("Error:" + str(e), status=401)

@csrf_exempt
def launchSim(request):
    launch_data = {}
    for k,v in request.POST.items():
        launch_data[k]=v
    
    TPI_Launch_Log.logTPIRequest(request)
    
    if TPIUtils.has_valid_signature(launch_data, url=settings.XLSIMS_LAUNCH_URL, key='bphsc2014'):
        return processLaunch(request, False)
    else:
        return HttpResponseRedirect(settings.SIMS_ROOT + 'message.html?op=auth')


def processLaunch(request, mockLaunch=False):
        param = request.POST.copy()
	print "xlsim launch"
        iSession = InteractiveSession.startInteractiveSession(param)
	print "startInteractiveSession  end"
        launchParam = iSession.getLaunchParam()
        if launchParam['custom_mode'] == 'setup':
            return HttpResponseRedirect(settings.SIMS_ROOT + 'message.html?op=settup')
        elif launchParam['custom_mode'] == 'review':
	    sjson = {}
	    sjson["user_id"] = iSession.user_id
            sjson["resource_id"] = iSession.resource_id
            sjson["context_id"] = iSession.context_id
            sjson["target_app"] = iSession.target_app
            sjson["launchParam"] = json.loads(iSession.launchParam)
            sjson["started"] = str(iSession.started)
            request.session['SIMReviewSession'] = sjson
            return HttpResponseRedirect(settings.SIMS_ROOT + 'classReview.html')
            
        try:
            url = SIMS_LAUNCH_TABLE[iSession.target_app]
        except:
            return HttpResponse('Error: the requested SIM could not be located ' + iSession.target_app, 404)
        try:
	    print "inside try -- json:1." + iSession.user_id + " 2." +  iSession.resource_id + " 3." +  iSession.context_id + " 4." +  iSession.target_app
            session = SimsSession.objects.get(iSession=iSession, active=True, topScore=False)
	    print "get simSession complete"
            session.start = timezone.now()
	    print "session.start=timezone.now():" + str( timezone.now())
            session.save()
        except Exception, e:
	    print "inside exception " + str(e)
            #there is no active SIM running so start an new unr
            allowedAttempts = int(request.POST['custom_attemptsallowed'])
	    print "inside exception before condition:" + str(allowedAttempts)  + " and " +  str(request.POST['custom_mode'])
            if allowedAttempts > 0 and request.POST['custom_mode'] == 'do':
                attemptCount = SimsSession.objects.filter(iSession=iSession).count()
		print "attemptCount" + str(attemptCount)
                if attemptCount >= allowedAttempts:
                    return HttpResponseRedirect(settings.SIMS_ROOT + 'message.html?op=attempts')
            session = SimsSession()
            #sessions from the emulator are marked as such so we treat them different for security reasons
            session.iSession = iSession;
            session.start = timezone.now()
            session.save();
        session.iSession = iSession
        
        sjson = {}
        sjson["user_id"] = iSession.user_id
        sjson["resource_id"] = iSession.resource_id
        sjson["context_id"] = iSession.context_id
        sjson["target_app"] = iSession.target_app
        sjson["launchParam"] = json.loads(iSession.launchParam)
        sjson["started"] = str(iSession.started) 
        
        ssjson ={}
        ssjson["iSession"] = sjson
        ssjson["customData"] = session.customData
        ssjson["active"] = session.active
        ssjson["isTest"] = session.isTest    
        ssjson["score"] = session.score
        ssjson["start"] = str(session.start)
        ssjson["end"] = str(session.end)
        ssjson["topScore"] = session.topScore       
        
        request.session['SIMSession'] = ssjson;
        
        if mockLaunch:
            #launched from the emulator, so we're sending a description of the state instead of redirecting
            param = session.iSession.getLaunchParam()
            data = {
                'user_id':request.POST['user_id'],
                'context_id':request.POST['context_id'],
                'sim_name':iSession.target_app,
                'user_name':param['custom_firstname'] + ' ' + param['custom_lastname'],
                'assignment':param['custom_assignmenttitle'],
                'url':url  
            }
            return HttpResponse(json.dumps(data), 'application/json')
        else:
            return HttpResponseRedirect(url);

@csrf_exempt
def getLaunchParams(request):
    args = request.POST;
    try:
        jsession = request.session['SIMSession']
        session = SimsSession.getSimSessionObjectFromJson(jsession)
    except:
        return HttpResponse('You do not have active session running', status=401)
    launchParam = session.iSession.getLaunchParam()
    blob = {
            'mode':launchParam['custom_mode'],
            'roles':launchParam['roles'],
            'assignment_title':launchParam['custom_assignmenttitle'],
            'first_name':launchParam['custom_firstname'],
            'last_name':launchParam['custom_lastname'],           
        }
    return HttpResponse(json.dumps(blob), 'application/json')
	
@csrf_exempt
def getReviewLaunchParams(request):
    args = request.POST;
    try:
        jsession = request.session['SIMSession']
        session = SimsSession.getSimSessionObjectFromJson(jsession)
    except:
        return HttpResponse('This is a test session message 2.', status=401)
    launchParam = session.iSession.getLaunchParam()
    blob = {
            'mode':launchParam['custom_mode'],
            'roles':launchParam['roles'],
            'assignment_title':launchParam['custom_assignmenttitle'],
            'first_name':launchParam['custom_firstname'],
            'last_name':launchParam['custom_lastname'],           
        }
    return HttpResponse(json.dumps(blob), 'application/json')

@csrf_exempt
def getState(request):
    try:
        jsession = request.session['SIMSession']
        session = SimsSession.getSimSessionObjectFromJson(jsession)
    except:
        return HttpResponse('You do not have an active session running', status=401)
    runs = SimsSession.objects.filter(iSession=session.iSession, active=False).order_by('-end')
    if len(runs) > 0:
        score = runs[0].score
    else:
        score = session.score
    attempts = len(runs) + 1
    duration = (timezone.now() - session.start).seconds
    data = {
        'score':score,
        'attempts':attempts,
        'duration':duration
    }
    return HttpResponse(json.dumps(data), 'application/json')
    
@csrf_exempt                
def getCustomData(request):
    try:
        jsession = request.session['SIMSession']
        session = SimsSession.getSimSessionObjectFromJson(jsession)
    except:
        return HttpResponse('You do not have an active session running', status=401)
    return HttpResponse(session.customData, 'application/json')

@csrf_exempt
def saveCustomData(request):
    data = request.POST['data']
    try:
        jsession = request.session['SIMSession']
        session = SimsSession.getSimSessionObjectFromJson(jsession)
    except:
        return HttpResponse('You do not have an active session running', status=401)
    session.customData = data
    request.session['SIMSession'] = session;
    session.save()
    return HttpResponse('', 'application/json')

@csrf_exempt    
def report(request):
    try:
	print "vinod report grade start"
        jsession = request.session['SIMSession']
        simSession = SimsSession.getSimSessionObjectFromJson(jsession)
    except:
        HttpResponse('Not Authorized', status=401)
    print "vinod report - 1"
    iSession = simSession.iSession
    print "vinod report - 2331"

    launchParam = iSession.getLaunchParam()
    print "vinod report - 33111"

    if launchParam['custom_mode'] != 'do':
        return HttpResponse('')
    print "vinod report - 12"    
    #get the 2 data points we are going to save
    score = float(request.POST['score'])
    time = float(request.POST['time'])
    time = int(time)
    print "vinod report - 13"
    #set custom data
    customData = request.POST.get('customData','')
    print "vinod report - 14"
    #get history to figure out attempts and top score
    runs = SimsSession.objects.filter(iSession__user_id=simSession.iSession.user_id, iSession__resource_id=simSession.iSession.resource_id, iSession__target_app=simSession.iSession.target_app, active=False).order_by('-score')
    #runs = SimsSession.objects.filter(iSession=simSession.iSession, active=False).order_by('-score')
    print "vinod report - 15"
    print "vinod report - 15 run length:" + str(len(runs)) 
    with transaction.atomic():
        if len(runs) > 0 and runs[0].score > score:
	    print "vinod report - 15 if runs[0].score=" + str(runs[0].score) + " score=" + str(score)
            topScore = runs[0].score
        else:
	    print "vinod report - 15 else score=" + str(score)
            topScore = score   
            simSession.topScore = True
            if len(runs) > 0:
		print "naveen-NM-runs[0].score=" + str(runs[0].score) + "runs.length=" + str(len(runs))
                SimsSession.objects.filter(pk=runs[0].pk).update(topScore=False)     
        print "vinod report - 16"
        attempts = len(runs) + 1
        simSession.score = score
        simSession.active = False
        simSession.customData = customData;
        simSession.end = timezone.now()
        simSession.start = simSession.end - datetime.timedelta(seconds=time)
        simSession.save();
	print "vinod report - 17"
    print "vinod report - 19"
    duration = int((simSession.end - simSession.start).seconds);
    print "vinod report - 18"
    for r in runs:
        duration += int((r.end - r.start).seconds)
    print "vinod report - 122"    
    sendTPIReport(topScore, duration, attempts, simSession.iSession.getLaunchParam())
    print "vinod report - 123"
    del request.session['SIMSession']
    print "vinod report - 124"
    return HttpResponse('')

    
    
def getStudentData(request):
    try:
        jiSession = request.session['SIMReviewSession']
        iSession = InteractiveSession().getSessionObjectFromJson(jiSession)
    except:
        HttpResponse('Not Authorized', status=401)
    param = iSession.getLaunchParam()
    if not 'Educator' in param['roles'] and not 'TeachingAssistant' in param['roles']:
        user_id = iSession.user_id
    else:
        try:
            user_id = request.GET['user_id']
        except:
            user_id = iSession.user_id    
    sessions = SimsSession.objects.filter(iSession__user_id=user_id, iSession__resource_id=iSession.resource_id, iSession__target_app=iSession.target_app, active=False)
    results = []
    totalDuration = 0
    avgScore = 0
    for s in sessions:
        time = round(float((s.end - s.start).seconds)/60, 1)
        score = s.score*100
        if len(s.customData) > 0:
            review=s.customData
        else:
            review=0				
        results.append({'score':score, 'duration':time,'review':review})
        totalDuration += time
        avgScore += score
    totalDuration = round(totalDuration, 1)
    jsonData = {'attempts':results, 'totalDuration':totalDuration}
    return HttpResponse(json.dumps(jsonData), 'application/json')


def getClassStats(request):
    
    try:
        jiSession = request.session['SIMReviewSession']
        iSession = InteractiveSession().getSessionObjectFromJson(jiSession)
    except:
        HttpResponse('Not Authorized', status=401)
    
    bestScores = 0
    bestDurations = 0
    allScores = 0
    allDurations = 0
    bestCount = 0
    allCount = 0
    runs = SimsSession.objects.filter(iSession__resource_id=iSession.resource_id, iSession__target_app=iSession.target_app, active=False)
    students = {}
    for r in runs:
        try:
            students[r.iSession.user_id]
        except:
            modes = r.iSession.getLaunchParam()['roles']
            if 'Learner' in modes:
                students[r.iSession.user_id] = ''
        allScores+=r.score
        duration = float((r.end - r.start).seconds)/60
        allDurations+=duration
        allCount+=1
        if r.topScore:
            bestScores+=r.score
            bestDurations+=duration
            bestCount+=1
    bestScores = round(float(bestScores*100)/bestCount, 2)
    bestDurations = round(float(bestDurations)/bestCount, 1)
    allScores = round(float(allScores*100)/allCount, 2)
    allDurations = round(float(allDurations)/allCount, 1)
    avgAttempts = round(float(len(runs))/len(students.keys()), 1)
    jsonData = {'runs':len(runs), 'avgBestScore':bestScores, 'avgBestDuration':bestDurations, 'avgScore':allScores, 'avgDuration':allDurations, 'avgAttempts':avgAttempts}
    return HttpResponse(json.dumps(jsonData), 'application/json')


def getStudents(request):    
    try:
        jiSession = request.session['SIMReviewSession']
        iSession = InteractiveSession().getSessionObjectFromJson(jiSession)
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if not 'Educator' in launchParam['roles'] and not 'TeachingAssistant' in launchParam['roles']:
        return HttpResponse('{}', status=401)            
    sessions = InteractiveSession.objects.filter(context_id=iSession.context_id, target_app=iSession.target_app, resource_id=iSession.resource_id)
    students = []
    for s in sessions:
        param = s.getLaunchParam();
        studentEntry = {'user_id':s.user_id, 'name':param['custom_firstname'] + ' ' + param['custom_lastname'], 'course_id':s.context_id, 'resource_id':iSession.resource_id}
        if iSession.user_id == s.user_id:
            studentEntry['currentStudent'] = True

	usrFound = False    
	for i in students:
	    if i['user_id'] == s.user_id:
		usrFound = True
		break        
	if usrFound == False:
            students.append(studentEntry)
        #students.append(studentEntry)
    return HttpResponse(json.dumps({'students':students, 'role':launchParam['roles']}))

'''Emulator functions'''

@csrf_exempt
def loginEmulator(request):
    #login handler for the emulator, this is not a high security operation
    #test sessions are segregated and teh emulator uses a common login
    un = request.POST['un']
    pw = request.POST['pw']
    if un == 'emulator' and pw == 'rhs_atm_Sims':
        response = HttpResponseRedirect('/atm_sims/simsEmulator/emulator.html')
        response.set_cookie('emulator', 'authorized')
        return response
    return HttpResponse('Not Authorized', status=401)


def getMySession(request):
    
    try:
        jsession = request.session['SIMSession']
        theSession = SimsSession.getSimSessionObjectFromJson(jsession)
    except:
        return HttpResponse('', status=401)
    param = theSession.iSession.getLaunchParam()
    data = {
        'user_id':theSession.iSession.user_id,
        'context_id':theSession.iSession.context_id,
        'user_name':param['custom_firstname'] + ' ' + param['custom_lastname'],
        'assignment':param['custom_assignmenttitle'],
        'sim_name':theSession.iSession.target_app,
        'url':SIMS_LAUNCH_TABLE[theSession.iSession.target_app],
        'session':request.session.session_key
    }
    return HttpResponse(json.dumps(data), 'application/json')

@csrf_exempt
def removeSession(request):
    user = request.POST['user_id']
    context = request.POST['context_id']
    sim = request.POST['sim_name']
    try:
        iSession = InteractiveSession.objects.get(user_id=user, target_app=sim, context_id=context)
    except:
        return HttpResponse('', status=401)

    with transaction.atomic():
        SimsSession.objects.filter(isTest=True, iSession=iSession).delete();
        if SimsSession.objects.filter(isTest=False).count() == 0:
            iSession.delete()
        try:
            jsession = request.session['SIMSession']
            mySession = SimsSession.getSimSessionObjectFromJson(jsession)
            if mySession.iSession == iSession.iSession:
                del request.session['SIMSession']
        except:
            pass
    return HttpResponse('', 'application/json')
   

@csrf_exempt
def mockLaunch(request):
    TPI_Launch_Log.logTPIRequest(request)
    return processLaunch(request, True)

def getSims(request):
    simList = []
    for sim in SIMS_LAUNCH_TABLE.keys():
        simList.append(sim)
    data = {'sims':simList}
    return HttpResponse(json.dumps(data), 'application/json')

def getSessions(request):
    #sessions = SimsSession.objects.filter(isTest=True)
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'syncdb', '--noinput'])    
    iSessions = InteractiveSession.objects.filter(simssession__isTest=False).distinct()
    data = {'sessions':[]}
    for s in iSessions:
        param = s.getLaunchParam()
        param['target_app'] = s.target_app
        #userName = param['custom_firstname'] + ' ' + param['custom_lastname']
        #assignment = param['custom_assignmenttitle']
        #data['sessions'].append({'id':s.pk, 'assignment':assignment, 'user_id':s.user_id, 'context_id':s.context_id, 'sim_name':s.target_app, 'user_name':userName})
        data['sessions'].append(param)
    return HttpResponse(json.dumps(data), 'application/json')
    
        
'''helper functions - not connected to a specific URL'''

def sendTPIReport(score, duration, count,params):

    extraParam = {
    
        'transactionId':uuid.uuid4(),                    
        'timeStamp': TPIUtils.timestamp(),
        'score': float(score) * float(params['custom_points_' + params['custom_currentquestion']]),
        'duration':duration,
        'submissionCount':count,
        'problem_guid':params['custom_target_' + params['custom_currentquestion']],
        'problemNumber':params['custom_currentquestion'],
        'dataSourceName':'CA',
    }   

    url = settings.OUTCOMES_URL
    body = TPIUtils.outcome_xml(params, **extraParam)
    auth = (settings.OUTCOMES_USER, settings.OUTCOMES_PW)
    resp = requests.post(url, data=body, auth=auth)
    msg = TPI_Launch_Log(message='TPI report : %d' % resp.status_code)
    msg.save()
    msg = TPI_Launch_Log(message=body)
    msg.save()    
    print body
    print 'resp:', resp, resp.content
    return body


def sendTPIReportBackDate(score, duration, count,params,c_date):

    extraParam = {
        'transactionId':uuid.uuid4(),
        'timeStamp': TPIUtils.timestampstr(c_date),
        'score': float(score) * float(params['custom_points_' + params['custom_currentquestion']]),
        'duration':duration,
        'submissionCount':count,
        'problem_guid':params['custom_target_' + params['custom_currentquestion']],
        'problemNumber':params['custom_currentquestion'],
        'dataSourceName':'CA',
    }

    url = settings.OUTCOMES_URL
    body = TPIUtils.outcome_xml(params, **extraParam)
    auth = (settings.OUTCOMES_USER, settings.OUTCOMES_PW)
    resp = requests.post(url, data=body, auth=auth)
    msg = TPI_Launch_Log(message='TPI report : %d' % resp.status_code)
    msg.save()
    msg = TPI_Launch_Log(message=body)
    msg.save()
    print body
    print 'resp:', resp, resp.content
    return body

