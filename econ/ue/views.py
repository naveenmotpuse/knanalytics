

from django.http import HttpResponse, HttpResponseRedirect
from gllaunch.models import *
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from models import *
from datacapture.models import *
from django.conf import settings
from knanalytics import TPIUtils
import uuid
import requests
from django.db.models import Q, Sum
import re
import string
import time

from econ.utils import CorsHttpDecorator



def wrapWithDelay(f):
    def wrapper(*args, **kwargs):
        time.sleep(2.5)
        return f(*args, **kwargs)
    return wrapper

# uncomment the line below to test slow server response...
# HttpResponse = wrapWithDelay(HttpResponse)

@csrf_exempt
def getUEState(request):
    
    addMessage('get state')
    print 'get state'
    try:
        iSession = request.session['interactives']['unemployment']
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    try:
        settings = UESettings.objects.get(class_id=launchParam['custom_resource_id'])
        levelMode = json.loads(settings.settings)['levels']
    except:
        levelMode = 'all' 
        
        
    if levelMode == 'all':
        ueState = InteractiveState.getOrCreateActiveState(iSession, 4, False)
    elif levelMode == '1_2':
        ueState = InteractiveState.getOrCreateActiveState(iSession, 2, False)
    else:
        ueState = InteractiveState.getOrCreateActiveState(iSession, 3, False)
        
    levels = InteractiveLevel.objects.filter(parent=ueState, completed=True).order_by('level')
    levelData = {}
    scores = []
    for i in range(1, ueState.levels + 1):
        scores.append(0)
        for l in levels:
            if l.level == i:
                scores[i - 1] = l.score
                levelData['level' + str(i)] = l.levelData
                break
        try:
            levelData['level' + str(i)]
        except:
            levelData['level' + str(i)] = ''     
    
    try:
        settings = UESettings.objects.get(class_id=launchParam['custom_resource_id'])
    except:
        settings = UESettings()
    
      
    #for testing and development only, LEVEL_LOCK should never be defined in production    
    try:
        if settings.LEVEL_LOCK:
            levelLock = LevelLock.objects.get(session=iSession).level
            if ueState.currentLevel > levelLock:
                ueState.currentLevel = levelLock
    except:
        pass
    
    #nav- end commnt code block
    
        
    try:
        customData = json.loads(ueState.customData)
    except:
        customData = {}
        
    history = ueState.getHistory()
    
    response = {
        'currentLevel':ueState.currentLevel, 
        'mode':launchParam['custom_mode'],
        'role':launchParam['roles'],
        'name':{'first':launchParam['custom_firstname'], 'last':launchParam['custom_lastname']},
        'data':levelData,
        'customData':customData,
        'scores':scores,
        'attemptsAllowed':float(launchParam['custom_attemptsallowed']),
        'attemptsCompleted':InteractiveLevel.objects.filter(parent__iSession=iSession).count()/4.0,
        'settings':json.loads(settings.settings),
        'history':history
    }
    request.session['ueHistory'] = history
    return HttpResponse(json.dumps(response), 'application/json')


@csrf_exempt        
def startUELevel(request):
    
    try:
        iSession = request.session['interactives']['unemployment']
    except:
        return HttpResponse('{}', status=401)
    history = request.session['ueHistory']
    params = json.loads(request.body)
    level =int(params['level'])

    #for testing and development only, LEVEL_LOCK should never be defined in production
    try:
        if settings.LEVEL_LOCK:
            levelLock = LevelLock.objects.get(session=iSession, level=settings.LEVEL_LOCK).level
            if level > levelLock:
                return HttpResponse('{}', 'application/json')
    except:
        pass

    ueState = InteractiveState.getOrCreateActiveState(iSession, 4, True)
    if not ueState.startLevel(level):
        return HttpResponse('{}', status=400)
    resp = {'level':level}
    return HttpResponse(json.dumps(resp), 'application/json')
    
    
@csrf_exempt
def saveUELevel(request):
    
    try:
        iSession = request.session['interactives']['unemployment']
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam();
    history = request.session['ueHistory']
    
    try:
        params = json.loads(request.body)
        level = params['level']
        score = params['score']
        levelData = params['data']
    except:
        return HttpResponse('{}', status=400)
    
    levelMode = 'all'

    try:
        settings = UESettings.objects.get(class_id=launchParam['resource_id'])
        levelMode = json.loads(settings.settings)['levels']
        if levelMode != 'all' and level > 3:
            return HttpResponse('{}', status=400)
        elif levelMode == '1_2' and level > 2:
            return HttpResponse('{}', status=400)            
    except:
        pass

    if levelMode == 'all':
        numLevels = 4
    elif levelMode == '1_2_3':
        numLevels = 3
    elif levelMode == '1_2':
        numLevels = 2
    ueState = InteractiveState.getOrCreateActiveState(iSession, numLevels, True)
    allowedAttempts = float(iSession.getLaunchParam()['custom_attemptsallowed'])
    attemptsRemaining = history['attempts'][level-1] < allowedAttempts or allowedAttempts==0
    op = ueState.getCurrentOp()    
    bestScore = True 
    if attemptsRemaining:
        bestScore = ueState.saveLevel(level=level, score=score, data=levelData)
        history['attempts'][level-1] = history['attempts'][level-1]+1
    else:
        bestScore = False
        ueState.cancelCurrentLevel()
    #new block
    '''bestScore = ueState.getBestScore()
    ueState.saveLevel(level=level, score=score, data=levelData)
    currentScore = ueState.getScore()
    highScore = bestScore == None or (bestScore != None and currentScore['total'] > bestScore['total'])'''

    #end new block
    isComplete = ueState.isComplete()
    if  isComplete and launchParam['custom_mode'] == 'do' and  attemptsRemaining and bestScore:
        sendTPIReport(ueState.iSession)

    request.session['ueHistory'] = history    
    resp = {'nextLevel':ueState.currentLevel, 'savedLevel':level, 'score':score, 'retry':op, 'highScore':bestScore, 'attempts':history['attempts']}
    return HttpResponse(json.dumps(resp), 'application/json')

    
@csrf_exempt
def saveUECustomData(request):   

    print 'saving custom data'
    try:
        iSession = request.session['interactives']['unemployment']
    except:
        return HttpResponse('{}', status=401)
    InteractiveState.objects.filter(iSession=iSession, active=True).update(customData=request.body)
    print 'saved custom data'
    return HttpResponse('{}', 'application/json')
    

@csrf_exempt
def restart(request):
    print 'restart level'
    try:
        iSession = request.session['interactives']['unemployment']
    except:
        return HttpResponse('{}', status=401)
    if InteractiveState.restart(iSession=iSession):
        return HttpResponse('{}', 'application/json')
    return HttpResponse('{}', status=403)
    
@CorsHttpDecorator
@csrf_exempt
def getUESettings(request):
    try:
        iSession = request.session['interactives']['unemployment']
        settingsObj = UESettings.objects.get(class_id=iSession.resource_id)
        settings = json.loads(settingsObj.settings)
        #set new defaults if not in the existing object
        try: 
            settings['levels'] 
        except: #old settings, so add the new defaults
            settings['levels'] = 'all'
    except:
        settings = {'useNaturalRate':True, 'levels':'all'}
    return HttpResponse(json.dumps(settings), 'application/json')
        
    
@csrf_exempt    
def saveUESettings(request):
    
    try:
        iSession = request.session['interactives']['unemployment']
        param = iSession.getLaunchParam()
        roles = param['roles']
        if 'Learner' in roles:
            raise Exception
    except:
        return HttpResponse('{}', status=401)
    
    rawData = request.body
    newSettings = json.loads(rawData)
    work = InteractiveState.objects.filter(iSession__resource_id=iSession.resource_id, iSession__target_app=iSession.target_app).count()
    if (work > 0):
        work = True
    else:
        work = False
    print 'ue/views.py saveUESettings work = ', str(work)
    #the class id is actually the resource_id (assignment)
    try:
        settings = UESettings.objects.get(class_id=iSession.resource_id)
    except:
        settings = UESettings()
        settings.class_id = iSession.resource_id
    if work:
        return HttpResponse('{}', status=401)
    settings.settings = json.dumps(newSettings)
    settings.save()
    return HttpResponse('{}', 'application/json')
 
 
'''@csrf_exempt
def quitUELevel(request):
    
    try:
        iSession = request.session['interactives']['unemployment']
    except:
        return HttpResponse('{}', status=401)
    ueState = InteractiveState.getActiveState(iSession)
    ueState.cancelCurrentLevel()
    return HttpResponse('{}', 'application/json')'''

    
@CorsHttpDecorator
def getStateUnemploymentData(request):
    state = request.GET['state']
    try:
        data = FredUnemploymentData.objects.get(state=state)
        return HttpResponse(data.data, 'application/json')
    except FredUnemploymentData.DoesNotExist:
        root = settings.ECON_LAUNCH_TABLE['unemployment'].replace('index.html', '')
        return HttpResponseRedirect(root + 'data/state_map_json/' + state + '_urn.json')

@CorsHttpDecorator
def getLaborParticipationData(request):
    try:
        data = FredUnemploymentData.objects.get(state='CIVPART')
        return HttpResponse(data.data, 'application/json')
    except FredUnemploymentData.DoesNotExist:
        return HttpResponseRedirect(settings.ECON_LAUNCH_TABLE['unemployment'] + 'data/us_labor_force.json')
        
@CorsHttpDecorator
def getCivilianUnemploymentData(request):
    try:
        data = FredUnemploymentData.objects.get(state='UNRATE')
        return HttpResponse(data.data, 'application/json')
    except FredUnemploymentData.DoesNotExist:
        return HttpResponseRedirect(settings.ECON_LAUNCH_TABLE['unemployment'] + 'data/us_unemployment.json')

@CorsHttpDecorator
def getNaturalUnemploymentData(request):
    try:
        data = FredUnemploymentData.objects.get(state='NROU')
        return HttpResponse(data.data, 'application/json')
    except FredUnemploymentData.DoesNotExist:
        return HttpResponseRedirect(settings.ECON_LAUNCH_TABLE['unemployment'] + 'data/us_nairu_long.json')
        

def getAggregates(request):
    try:
        iSession = request.session['interactives']['unemployment']
    except:
        return HttpResponse('{}', status=401)

    launchParam = iSession.getLaunchParam()
    if 'Learner' in launchParam['roles']:
        return HttpResponse('{}', status=401)

    students = {}
    aggs = [{'score':0, 'duration':0, 'count':0, 'levelScore':0} for idx in range(4)]

    results = InteractiveLevel.objects.filter(parent__iSession__resource_id=iSession.resource_id, parent__iSession__target_app=iSession.target_app, active=False)

    for r in results:
        params = r.parent.iSession.getLaunchParam()

        if 'Learner' in params['roles']:

            try:
                levelScore = json.loads(r.levelData)['levelScore']
            except KeyError, ValueError:
                levelScore = 0

            duration = (r.closed - r.started).seconds

            try:
                sScores = students[r.parent.iSession.user_id]
            except KeyError:
                sScores = {}

            try:
                currentScore = sScores[str(r.level)]
                if r.score > currentScore[0]:
                    sScores[str(r.level)] = (r.score, duration, levelScore)
                    students[r.parent.iSession.user_id] = sScores
            except:
                sScores[str(r.level)] = (r.score, duration, levelScore)
                students[r.parent.iSession.user_id] = sScores
                    
            params = r.parent.iSession.getLaunchParam()
            aggs[r.level-1]['score'] += r.score
            aggs[r.level-1]['levelScore'] += levelScore
            aggs[r.level-1]['duration'] += float((r.closed - r.started).seconds)/60
            aggs[r.level-1]['count']+=1

    highScoreCount = [0, 0, 0, 0]
    highScores = [{'score':0, 'duration':0, 'levelScore':0} for idx in range(4)]

    for s in students.values():
        for idx in range(0, 4):
            try:
                highScores[idx]['score'] += s[str(idx+1)][0]
                highScores[idx]['duration'] += s[str(idx+1)][1]
                highScores[idx]['levelScore'] += s[str(idx+1)][2]
                highScoreCount[idx]+=1
            except:
                pass

    highScore = 0;
    highDuration = 0;
    if len(students) > 0:
        for idx in range(3, -1, -1):
            if highScores[idx]['duration'] == 0:
                del highScores[idx]    
        for idx in range(0,len(highScores)):
            highScores[idx]['score'] = highScores[idx]['score']/float(len(students)*100)
            highScores[idx]['duration'] = round(highScores[idx]['duration']/float(len(students)*60), 1)
            highScores[idx]['levelScore'] = highScores[idx]['levelScore']/float(len(students))

            highScore+= highScores[idx]['score']
            highDuration+=highScores[idx]['duration']
        # highDuration = round(highDuration, 1)

    avgDuration = 0
    avgScore = 0
    for idx in range(3, -1, -1):
        if aggs[idx]['count'] == 0:
            del aggs[idx]
    for idx in range(0, len(aggs)):
        if aggs[idx]['count'] > 0:
            aggs[idx]['score'] = aggs[idx]['score']/(float(aggs[idx]['count'])*100)
            aggs[idx]['duration'] = round(aggs[idx]['duration']/float(aggs[idx]['count']), 1)          
            aggs[idx]['levelScore'] = aggs[idx]['levelScore']/float(aggs[idx]['count'])
            avgDuration+=aggs[idx]['duration']
            avgScore+=aggs[idx]['score']
    
    jsonData = {
                'levels':aggs,
                'duration':round(avgDuration, 1),
                'score':avgScore,
                'highscores':highScores,
                'highScore':highScore,
                'highDuration':round(highDuration, 1),
        }

    return HttpResponse(json.dumps(jsonData), 'application/json')


def getStudents(request):    
    try:
        iSession = request.session['interactives']['unemployment']
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if 'Learner' in launchParam['roles']:
        return HttpResponse('{}', status=401)            
    sessions = InteractiveSession.objects.filter(context_id=iSession.context_id, target_app=iSession.target_app, resource_id=iSession.resource_id)
    students = []
    for s in sessions:
        param = s.getLaunchParam();
        # if 'Learner' in s.getLaunchParam()['roles']:
        if True:
            studentEntry = {'user_id':s.user_id, 'name':param['custom_firstname'] + ' ' + param['custom_lastname'], 'course_id':s.context_id, 'resource_id':iSession.resource_id}
            if iSession.user_id == s.user_id:
                studentEntry['currentStudent'] = True
            students.append(studentEntry)
    return HttpResponse(json.dumps({'students':students}))
        
        
def getStudentData(request):
    try:
        iSession = request.session['interactives']['unemployment']
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if 'Learner' in launchParam['roles']:
        return HttpResponse('{}', status=401)

    user_id = request.GET['user_id']

    # set up to capture the highest score info for each level...
    highScores = [{'score':0, 'duration':0, 'levelScore':0} for i in range(4)]

    results = InteractiveLevel.objects.filter(parent__iSession__user_id=user_id, parent__iSession__resource_id=iSession.resource_id, parent__iSession__target_app=iSession.target_app, active=False).order_by('started')
    for r in results:
        duration = (r.closed - r.started).seconds
        score = r.score         # this is a number from < 100 which represents the partial total for ALL levels; e.g. 29.41
        levelScore = score      # in case we are dealing with old data
        try:
            levelScore = json.loads(r.levelData)['levelScore']  # this is 100 if they got every question right for this level
        except KeyError, ValueError:
            levelScore = score

        levelIndex = r.level -1
        levelHighScore = highScores[levelIndex]

        if score > levelHighScore['score']:
            # print "level %d %f -> %f" % (levelIndex, levelHighScoreData['score'], score)
            levelHighScore['score'] = float(score)
            levelHighScore['duration'] = float(duration)/60
            levelHighScore['levelScore'] = levelScore

    highScore = 0
    highDuration = 0
    # highLevelScore = 0

    for idx in range(3, -1, -1):
        if highScores[idx]['duration'] == 0:
            del highScores[idx]
    
    # for idx in range(0, len(highScores)):
    for levelHighScore in highScores:
        levelHighScore['score'] /= 100.0        # to be consistent with XL reporting, this will be a number from 0..1
        highScore += levelHighScore['score']    # this sum will be my highest score in 0..1 as reported to XL
        
        levelHighScore['duration'] = round(levelHighScore['duration'], 1)
        highDuration += levelHighScore['duration']
    
    highDuration = round(highDuration, 2)
    
    jsonData = getResultAggregates(results)     # this gets the averages for each level with various details
    jsonData['highScores'] = highScores
    jsonData['highScore'] = highScore
    jsonData['highDuration'] = highDuration
    return HttpResponse(json.dumps(jsonData), 'application/json')
    
    
def getResultAggregates(results):

    aggs = [{'score':0, 'duration':0, 'count':0, 'levelScore': 0} for idx in range(4)]    

    for r in results:
        params = r.parent.iSession.getLaunchParam()
        aggs[r.level-1]['score'] += r.score
        aggs[r.level-1]['duration'] += float((r.closed - r.started).seconds)/60
        aggs[r.level-1]['count']+=1
        levelScore = 0
        try:
            levelScore = json.loads(r.levelData)['levelScore']
        except KeyError, ValueError:
            levelScore = r.score
        aggs[r.level-1]['levelScore'] += levelScore


    avgDuration = 0
    avgScore = 0
    for idx in range(3, -1, -1):
        if aggs[idx]['count'] == 0:
            del aggs[idx]

    for idx in range(0, len(aggs)):
        count = aggs[idx]['count']
        if count > 0:
            aggs[idx]['score'] = aggs[idx]['score']/(float(aggs[idx]['count'])*100)
            aggs[idx]['duration'] = round(aggs[idx]['duration']/float(aggs[idx]['count']), 1)            
            aggs[idx]['levelScore'] = aggs[idx]['levelScore']/float(aggs[idx]['count'])        
            avgDuration+=round(aggs[idx]['duration'], 2)
            avgScore+= aggs[idx]['score']

    resultData = {'levels':aggs,
                'duration':round(avgDuration, 1),
                'score': avgScore}
    return resultData

 
def sendTPIReport(iSession):
    
    params = json.loads(iSession.launchParam)
    state = InteractiveState.objects.get(iSession=iSession, active=True)
    levels = InteractiveLevel.objects.filter(parent=state, completed=True)        
    score = 0
    for l in levels:
        score += l.score
    score = float(score)/100
    score = score * float(params['custom_points_' + params['custom_currentquestion']])

    completedLevels = InteractiveLevel.objects.filter(Q(restarted=True) | Q(completed=True), parent=state)
    count = len(completedLevels)/4
    if len(completedLevels) % 4 > 0:
        count += 1
    duration = 0
    for l in completedLevels:
        duration += int((l.closed - l.started).seconds)
    extraParam = {
    
        'transactionId':uuid.uuid4(),                    
        'timeStamp': TPIUtils.timestamp(),
        'score':score,
        'duration':duration,
        'submissionCount':count,
        'problem_guid':params['custom_target_' + params['custom_currentquestion']],
        'problemNumber':params['custom_currentquestion'],
        'dataSourceName':'UE',
    }    
    
    url = settings.OUTCOMES_URL
    body = TPIUtils.outcome_xml(params, **extraParam)
    auth = (settings.OUTCOMES_USER, settings.OUTCOMES_PW)
    print 'body:', body
    msg = TPI_Launch_Log(message=body)
    msg.save()
    resp = requests.post(url, data=body, auth=auth)
    print 'resp:', resp, resp.content
    return resp

def addMessage(message):
    msg = TPI_Launch_Log()
    msg.message = message
    msg.save()





    
