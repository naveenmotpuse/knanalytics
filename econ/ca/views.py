
from django.http import HttpResponse
from econ.ca.models import *
from gllaunch.models import *
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from knanalytics import TPIUtils
import requests
import uuid
from django.conf import settings
from django.db.models import Q

scoreWeights = [0.1, 0.15, 0.25, 0.50]


def generateCAStateObject(caState):
                                   
    caData = {}
    caData['currentLevel'] = caState.currentLevel
    caData['tool'] = caState.tool
    caData['surplusFish'] = caState.surplusFish
    caData['surplusWood'] = caState.surplusWood
    launchParam = caState.iSession.getLaunchParam()
    caData['mode'] = launchParam['custom_mode']
    
    try:
        caData['levelSetting'] = LevelSetting.objects.get(class_id=caState.iSession.resource_id).setting
    except:
        caData['levelSetting'] = 'all'
    
    l1 = None if caState.l1Completed == None else str(caState.l1Completed)
    l2 = None if caState.l1Completed == None else str(caState.l2Completed)
    l3 = None if caState.l1Completed == None else str(caState.l3Completed)
    l4 = None if caState.l1Completed == None else str(caState.l4Completed)
    
    levels = []
    levels.append({'score':caState.l1Score, 'completed':l1})
    levels.append({'score':caState.l2Score, 'completed':l2})
    levels.append({'score':caState.l3Score, 'completed':l3})
    levels.append({'score':caState.l4Score, 'completed':l4})
    caData['levels'] = levels
    name = {'first':launchParam['custom_firstname'], 'last':launchParam['custom_lastname']}
    caData['name'] = name
    caData['attemptsAllowed'] = int(launchParam['custom_attemptsallowed']);
    caData['attemptsCompleted'] = CAState.objects.filter(iSession=caState.iSession).count();
    return caData                          


@csrf_exempt
def getState(request):
    
    print 'get state'
    try:
        jiSession = request.session['interactives']['comparative_advantage']
	iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    except:
        return HttpResponse('', status=401)

    launchParam = iSession.getLaunchParam();
    mode = launchParam['custom_mode']
    if mode == 'practice' or mode == 'preview':
        state = {
                 'currentLevel':1, 
                 'tool':'none', 
                 'surplusFish':0, 
                 'surplusWood':0, 
                 'mode':mode,
                 'name':{'first':launchParam['custom_firstname'], 'last':launchParam['custom_lastname']},
                 'levels':[
                      {'score':0, 'completed':None},
                      {'score':0, 'completed':None},
                      {'score':0, 'completed':None},
                      {'score':0, 'completed':None},
                 ],
                'attemptsAllowed':0,
                'attemptsCompleted':0,
                }
        return HttpResponse(json.dumps(state), 'application/json')
    elif mode == 'review':
        caState = CAState.getActiveState(iSession)
        caBestState = caState.getBestState()
        caData = generateCAStateObject(caBestState)
        # force user to review screen 
        caData['currentLevel'] = 5
        # The following disables retry
        caData['attemptsAllowed']= 1
        caData['attemptsCompleted'] = 2
        return HttpResponse(json.dumps(caData), 'application/json')
    else: # mode is do
        # If active state is completed, show best score on Summary screen, not most recent
        # NOTE: If the desired behavior is to not save intermediate results after one successful 
        # complettion, then caState should always be caBestState.
        caState = CAState.getActiveState(iSession)
        if caState.currentLevel == 5:
            caBestState = caState.getBestState()
            caData = generateCAStateObject(caBestState)
        else:
            caData = generateCAStateObject(caState)
        return HttpResponse(json.dumps(caData), 'application/json')
        
        
@csrf_exempt
def saveLevel(request):
    
    print 'save level'
    try:
        jiSession = request.session['interactives']['comparative_advantage']
	iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    except:
        return HttpResponse(status=401)
    launchParam = iSession.getLaunchParam()
    mode = launchParam['custom_mode']
    totalAttempts = CAState.objects.filter(iSession=iSession).count()
    #return HttpResponse('naveen:'+ str(totalAttempts), 'application/json')
    allowedAttempts = int(launchParam['custom_attemptsallowed'])    
    if mode in ['practice', 'preview','review'] or (allowedAttempts > 0 and totalAttempts > allowedAttempts):
        return HttpResponse('{}', 'application/json')
    data = json.loads(request.body)
    allowedAttempts = int(launchParam['custom_attemptsallowed'])
    caState = CAState.getActiveState(iSession)
    #return HttpResponse('naveen22:'+ str(totalAttempts), 'application/json')
    if not caState.saveCurrentLevel(data):
        return HttpResponse('{}', status=403)
    #return HttpResponse('naveen3333:', 404)
    if CAState.objects.filter(iSession=iSession).count() > 1:
        isRetry = True
    else:
        isRetry = False
    if  caState.completed and launchParam['custom_mode'] == 'do':
	#return HttpResponse('naveen333:', 404)
        bestScore = caState.getBestScore()
        #return HttpResponse('naveen33:'+ str(bestScore), 'application/json')
        if caState.totalScore() <= bestScore:
            return HttpResponse(json.dumps({'bestScore':False, 'retry':isRetry}))
        #reporting scores to tpi will go here
        sendTPIReport(caState, launchParam)
    return HttpResponse(json.dumps({'bestScore':True, 'retry':isRetry}), 'application/json')


@csrf_exempt
def startLevel(request):

    print 'start level'
    try:
        jiSession = request.session['interactives']['comparative_advantage']
	iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    except:
        return HttpResponse(status=401)
    launchParam = iSession.getLaunchParam();
    mode = launchParam['custom_mode']
    totalAttempts = CAState.objects.filter(iSession=iSession).count()
    allowedAttempts = int(launchParam['custom_attemptsallowed'])
    if mode in ['practice', 'preview', 'review'] or (allowedAttempts > 0 and totalAttempts > allowedAttempts):
        return HttpResponse('{}', 'application/json')
    caState = CAState.getActiveState(iSession)
    level = int(request.body);
    
    #for testing and development only, LEVEL_LOCK should never be defined in production
    try:
        if settings.LEVEL_LOCK:
            levelLock = LevelLock.objects.get(session=iSession, level=settings.LEVEL_LOCK)
            if level > levelLock:
                return HttpResponse('{}', 'application/json')
    except:
        pass


    if not caState.startLevel(level):
        return HttpResponse('{}', status=403)
    return HttpResponse('{}', 'application/json')


@csrf_exempt
def quitLevel(request):
    
    print 'quit level'
    try:
        jiSession = request.session['interactives']['comparative_advantage']
	iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    mode = launchParam['custom_mode']
    if mode in ['practice', 'preview', 'review']:
        return HttpResponse('{}', 'application/json')    
    caState = CAState.getActiveState(iSession)
    caState.cancelCurrentLevel()
    return HttpResponse('{}', 'application/json')


@csrf_exempt
def replay(request):
    
    print 'replay'
    try:
        jiSession = request.session['interactives']['comparative_advantage']
	iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam();
    mode = launchParam['custom_mode']
    if mode == 'do':
        caState = CAState.restart(iSession)
        obj = generateCAStateObject(caState)
    else:
        launchParam = json.loads(iSession.launchParam)
        obj = {
                 'currentLevel':1, 
                 'tool':'none', 
                 'surplusFish':0, 
                 'surplusWood':0, 
                 'mode':mode,
                 'name':{'first':launchParam['custom_firstname'], 'last': launchParam['custom_lastname']},
                 'levels':[
                      {'score':0, 'completed':None},
                      {'score':0, 'completed':None},
                      {'score':0, 'completed':None},
                      {'score':0, 'completed':None},
                 ],
                }        
    return HttpResponse(json.dumps(obj), 'application/json')

    
def sendTPIReport(caState, params):

    print 'send TPI Report'
    try:
        mode = LevelSetting.objects.get(class_id=caState.iSession.resource_id).setting
    except:
        print 'Failed to get level setting'
        mode = 'all'
    if mode == 'all':
        score = (scoreWeights[0]*caState.l1Score + 
                scoreWeights[1]*caState.l2Score + 
                scoreWeights[2]*caState.l3Score + 
                scoreWeights[3]*caState.l4Score)/100
    elif mode == '1to3':
        score = (scoreWeights[0]*caState.l1Score + 
                scoreWeights[1]*caState.l2Score + 
                scoreWeights[2]*caState.l3Score)/50
    else:
        score = caState.l4Score/100
    score = score * float(params['custom_points_' + params['custom_currentquestion']])
    levels = CALevel.objects.filter(parent__iSession=caState.iSession, completed=True)
    duration = 0
    for l in levels:
        duration += int((l.closed - l.started).seconds)
    count = CAState.objects.filter(iSession=caState.iSession).count()
    extraParam = {
    
        'transactionId':uuid.uuid4(),                    
        'timeStamp': TPIUtils.timestamp(),
        'score':score,
        'duration':duration,
        'submissionCount':count,
        'problem_guid':params['custom_target_' + params['custom_currentquestion']],
        'problemNumber':params['custom_currentquestion'],
        'dataSourceName':'CA',
    }    
    url = settings.OUTCOMES_URL
    body = TPIUtils.outcome_xml(params, **extraParam)
    auth = (settings.OUTCOMES_USER, settings.OUTCOMES_PW)
    # print body
    resp = requests.post(url, data=body, auth=auth)
    print 'resp:', resp, resp.content
    return resp


def getLevelSetting(request):
    
    print 'get settings'
    jiSession = request.session['interactives']['comparative_advantage']
    iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    try:
        setting = LevelSetting.objects.get(class_id=iSession.resource_id)
        return HttpResponse('{"levelSetting":"' + setting.setting + '"}', 'application/json')
    except:
        return HttpResponse('{"levelSetting":"all"}', 'application/json')

@csrf_exempt
def saveLevelSetting(request):
    
    print 'save setting'
    jiSession = request.session['interactives']['comparative_advantage']
    iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    #return HttpResponse(iSession__resource_id, 404)
    launchParam = iSession.getLaunchParam()
    #return HttpResponse(launchParam['roles'], 404)
    roles = launchParam['roles']
    if 'Learner' in roles:
        return HttpResponse('{}', status=401)
    newSetting =request.body
    work = CAState.objects.filter(iSession__resource_id=iSession.resource_id).count()
    if work > 0:
        return HttpResponse('{}', status=401)
    #using resource_id for the class id
    try:
        setting = LevelSetting.objects.get(class_id=iSession.resource_id)
        setting.setting = newSetting
    except LevelSetting.DoesNotExist:
        setting = LevelSetting(setting=newSetting, class_id=iSession.resource_id)
    setting.save()
    return HttpResponse('{}', 'application/json')


def getStudents(request):    
    try:
        jiSession = request.session['interactives']['comparative_advantage']
	iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if 'Learner' in launchParam['roles']:
        return HttpResponse('{}', status=401)            
    sessions = InteractiveSession.objects.filter(context_id=iSession.context_id, target_app=iSession.target_app, resource_id=iSession.resource_id)
    students = []
    for s in sessions:
        param = s.getLaunchParam();
        studentEntry = {'user_id':s.user_id, 'name':param['custom_firstname'] + ' ' + param['custom_lastname'], 'course_id':s.context_id, 'resource_id':iSession.resource_id}
        if iSession.user_id == s.user_id:
            studentEntry['currentStudent'] = True
        students.append(studentEntry)
    return HttpResponse(json.dumps({'students':students}))


def getAggregates(request):
    try:
        jiSession = request.session['interactives']['comparative_advantage']
	iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if 'Learner' in launchParam['roles']:
        return HttpResponse('{}', status=401)         
    
    try:
        setting = LevelSetting.objects.get(class_id=iSession.resource_id).setting
    except:
        setting = 'all'
                  
    students = {}
    states = CAState.objects.filter(~Q(completed=None), iSession__resource_id=iSession.resource_id, iSession__context_id=iSession.context_id)
    for s in states:
        sLaunchParam = s.iSession.getLaunchParam()
        if 'Learner' in sLaunchParam['roles']:
            user_id = s.iSession.user_id
            try:
                students[user_id].append(s)
            except:
                students[user_id] = [s]
    
    highScore = 0
    highScoreDuration = 0
    highScoreCount = 0
    highScoreSessions = []
    highScoreLevels = []
    averageScore = 0
    averageDuration = 0
    
    for student in students.values():
        studentHighScore = 0
        for i in range(0, len(student)):
            s = student[i]
            score = s.l1Score*scoreWeights[0] + s.l2Score*scoreWeights[1] + s.l3Score*scoreWeights[2] + s.l4Score*scoreWeights[3]
            if setting != 'all':
                score *= 2
            if score > studentHighScore:
                studentHighScore = score                
                highSession = s
        highScore += studentHighScore
        highScoreSessions.append(highSession)
    
    highScore = highScore/len(students)

    levels = CALevel.objects.filter(parent__iSession__resource_id=iSession.resource_id, parent__iSession__context_id=iSession.context_id, completed=True)
    levelData = []
    
    for idx in range(0, 4):
        levelData.append({'score':0, 'duration':0, 'count':0})
        highScoreLevels.append({'score':0, 'duration':0, 'count':0})
    
    for l in levels:
        if 'Learner' in l.parent.iSession.getLaunchParam()['roles']:
            idx = l.level-1
            duration = float((l.closed - l.started).seconds)/60
            if l.parent in highScoreSessions:
                highScoreLevels[idx]['count']+=1
                highScoreLevels[idx]['score']+=l.score
                highScoreLevels[idx]['duration']+=duration    
                highScoreCount += 1
            levelData[idx]['score'] += l.score
            levelData[idx]['count'] += 1
            levelData[idx]['duration'] += duration
    
    for idx in range(3, -1, -1):
        if levelData[idx]['count'] == 0:
            del levelData[idx]      
        else:
            levelData[idx]['score'] = round(levelData[idx]['score']/float(levelData[idx]['count']), 2)
            levelData[idx]['duration'] = round(float(levelData[idx]['duration'])/levelData[idx]['count'], 1)
            averageDuration += levelData[idx]['duration']
        if highScoreLevels[idx]['count'] == 0:
            del highScoreLevels[idx]
        else:
            highScoreLevels[idx]['score'] = round(highScoreLevels[idx]['score']/float(highScoreLevels[idx]['count']), 2)
            highScoreLevels[idx]['duration'] = round(float(highScoreLevels[idx]['duration'])/highScoreLevels[idx]['count'], 1)
            highScoreDuration += highScoreLevels[idx]['duration']
    if len(levelData) == 4:
        for i in range(0, 4):
            averageScore += levelData[i]['score']*scoreWeights[i]
    elif len(levelData) == 3:
        for i in range(0, 3):
            averageScore += levelData[i]['score']*scoreWeights[i]
        averageScore *= 2
    elif len(levelData) == 1:
        averageScore = levelData[0]['score']
    else:
        averageScore = None
        
    highScoreDuration = round(highScoreDuration, 1)
    highScore = round(float(highScore), 2)  
    averageDuration = round(averageDuration, 1)
    if averageScore:
        averageScore = round(averageScore, 2) 
    jsonData = {'duration':averageDuration, 
                'score':averageScore, 
                'highDuration':highScoreDuration, 
                'highScore':highScore,
                'levels':levelData,
                'highscores':highScoreLevels}
    return HttpResponse(json.dumps(jsonData), 'application/json')
                
                
def getStudentData(request):
    try:
        jiSession = request.session['interactives']['comparative_advantage']
	iSession = InteractiveSession.getSessionObjectFromJson(jiSession)
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if 'Learner' in launchParam['roles']:
        return HttpResponse('{}', status=401)                
    user_id = request.GET['user_id']
    highScores = [{'score':0, 'duration':0}, {'score':0, 'duration':0}, {'score':0, 'duration':0}, {'score':0, 'duration':0}]
    results = CAState.objects.filter(~Q(completed=None), iSession__user_id=user_id, iSession__target_app=iSession.target_app, iSession__resource_id=iSession.resource_id)
    if len(results) == 0:
        return HttpResponse('{"levels":[]}', 'application/json')
    try:
        setting = LevelSetting.objects.get(class_id=iSession.resource_id).setting
    except:
        setting = 'all'
    
    print 'getStudentData: setting = ', setting

    highScore = 0
    highState = None
    highDuration = 0
    for r in results:
        score = r.l1Score*scoreWeights[0] + r.l2Score*scoreWeights[1] + r.l3Score*scoreWeights[2] + r.l4Score*scoreWeights[3]
        print 'getStudentData: score for each result state - ', score
        if (setting != 'all'):
            score *= 2
        if score > highScore:
            highScore = score
            highState = r
    levelData = []
    totalScore = 'not completed'
    count = 0
    

    highScores[0]['score'] = round(float(highState.l1Score), 2)
    highScores[1]['score'] = round(float(highState.l2Score), 2)
    highScores[2]['score'] = round(float(highState.l3Score), 2)
    highScores[3]['score'] = round(float(highState.l4Score), 2)
    
    highLevels = CALevel.objects.filter(parent=highState).order_by('level')
    for idx in range(0, len(highLevels)):
        highScores[idx]['duration'] = round(float((highLevels[idx].closed - highLevels[idx].started).seconds)/60, 1)
        highDuration += highScores[idx]['duration']
    for idx in range(3, -1, -1):
        if highScores[idx]['score'] == 0:
            del highScores[idx]

    try:
        # levels = CALevel.objects.filter(parent=highState)
        for idx in range(0, 4):
            levelData.append({'score':0, 'duration':0, 'count':0})
        levels = CALevel.objects.filter(~Q(parent__completed=None), parent__iSession=highState.iSession, completed=True)
        if setting == 'all':
            count = len(levels)/4
        elif setting == 'only4':
            count = len(levels)
        else:
            count = len(levels)/3
        totalScore = 0
        for l in levels:
            idx = l.level-1
            levelData[idx]['score'] += l.score
            levelData[idx]['duration'] += round(float((l.closed - l.started).seconds)/60, 1)
            levelData[idx]['count'] += 1
            if setting == 'all':
                totalScore += l.score*scoreWeights[idx]
            elif setting == 'only4':
                totalScore += l.score
            else:
                totalScore += l.score*scoreWeights[idx]*2
            print 'getStudentData: allAttempts level, levelData, totalScore = ', l.level, levelData, totalScore                
        for idx in range(3, -1, -1):
            if levelData[idx]['count'] == 0:
                del levelData[idx]
        if len(levelData) == 0:
            totalDuration = 'not completed'
        else:
            totalDuration = 0
        for idx in range(0, len(levelData)):
            levelData[idx]['score'] = round(float(levelData[idx]['score'])/(levelData[idx]['count']), 2)
            levelData[idx]['duration'] = levelData[idx]['duration']/levelData[idx]['count']
            totalDuration += levelData[idx]['duration']
    except:
        print 'getStudentData: exception thrown but passed on'
        pass
    highDuration = round(highDuration, 1)
    jsonData = {}
    jsonData['levels'] = levelData
    jsonData['highScores'] = highScores
    jsonData['highScore'] = round(float(highScore), 2)
    jsonData['highDuration'] = highDuration
    if count > 0:
        jsonData['score'] = round(float(totalScore)/(count), 2)
        jsonData['duration'] = totalDuration
    else:
        jsonData['score'] = 'not completed'
        jsonData['duration'] = 'not completed'
        
    return HttpResponse(json.dumps(jsonData), 'application/json')
