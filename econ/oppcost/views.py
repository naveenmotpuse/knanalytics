import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from econ.oppcost.models import OppCostSettings
from econ.utils import CorsHttpDecorator
from knanalytics import TPIUtils
from django.db.models import Q

from datacapture.models import InteractiveState, InteractiveLevel
from gllaunch.models import InteractiveSession, TPI_Launch_Log
from django.conf import settings


@CorsHttpDecorator
def getOppCostState(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['opportunity_cost']
        launchParam = iSession.getLaunchParam()
        settingObj = OppCostSettings.getorCreateSettings(class_id=launchParam['custom_resource_id'])
    except:
        return HttpResponse(status=401)
    level_settings = json.loads(settingObj.settings)
    levelCount = sum(json.loads(settingObj.settings).values())
    activated_levels = [int(item[0].split('level')[1]) for item in level_settings.items() if item[1]]
    oppCostState = InteractiveState.getOrCreateInteractiveState(
                                        iSession=iSession,
                                        activated_levels=activated_levels,
                                        levelCount=levelCount,
                                        )
    levels = InteractiveLevel.objects.filter(parent=oppCostState,
                                             completed=True).order_by('level')
    levelData = {}
    scores = [0, 0, 0]
    for i in activated_levels:
        for l in levels:
            if l.level == i:
                scores[i-1] = l.score
                levelData['level%d' % i] = l.levelData
                break
        try:
            levelData['level%d' % i]
        except:
            levelData['level%d' % i] = ''
    try:
        customData = json.loads(oppCostState.customData)
    except:
        customData = {}
    history = oppCostState.getHistory()
    response = {
                'currentLevel': oppCostState.currentLevel, 
                'mode': launchParam['custom_mode'],
                'name': {'first': launchParam['custom_firstname'],
                         'last': launchParam['custom_lastname']
                         },
                'data': levelData,
                'customData': customData,
                'scores': scores,
                'attemptsAllowed': float(launchParam['custom_attemptsallowed']),
                'attemptsCompleted': InteractiveLevel.objects.filter(parent__iSession=iSession,completed=True).count()/oppCostState.levels,
                'settings': level_settings,
                'history': history
                }
    request.session['oppcostHistory'] = history
    return HttpResponse(json.dumps(response), 'application/json')


@CorsHttpDecorator
def startOppCostLevel(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['opportunity_cost']
    except:
        return HttpResponse(status=401)
    try:
        level = int(request.GET['level'])
    except:
        return HttpResponse(status=400)
    oppCostState = InteractiveState.objects.get(iSession=iSession, active=True)
    if not oppCostState.startLevel(level):
        return HttpResponse(status=400)
    return HttpResponse(status=200)


@csrf_exempt
@CorsHttpDecorator
def saveOppCostLevel(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['opportunity_cost']
    except:
        return HttpResponse(status=401)
    history = request.session['oppcostHistory']
    try:
        params = json.loads(request.body)
        level = params['level']
        score = params['score']
        levelData = params['data']
    except:
        return HttpResponse(status=400)
    oppCostState = InteractiveState.objects.get(iSession=iSession, active=True)
    activated_levels = json.loads(oppCostState.activated_levels)
    bestScore = oppCostState.saveLevel(level=level, score=score, data=levelData)
    history['attempts'][activated_levels.index(level)] += 1
    if oppCostState.isComplete() and bestScore:
        TPIUtils.sendTPIReport(oppCostState, oppCostState.levels)
    request.session['oppcostHistory'] = history
    response = {'nextLevel': oppCostState.currentLevel,
                'savedLevel': level,
                'score': score,
                'retry': oppCostState.getCurrentOp(),
                'highScore': bestScore,
                'attempts': history['attempts']
                }
    return HttpResponse(json.dumps(response),
                        content_type='application/json',
                        status=200
                        )


@csrf_exempt
@CorsHttpDecorator
def saveOppCostCustomData(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['opportunity_cost']
    except:
        return HttpResponse(status=401)
    oppCostState = InteractiveState.objects.get(iSession=iSession,
                                                active=True
                                                )
    oppCostState.customData = request.body
    oppCostState.save()
    return HttpResponse(status=200)


@CorsHttpDecorator
def restart(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['opportunity_cost']
    except:
        return HttpResponse(status=401)
    if InteractiveState.restart(iSession=iSession):
        return HttpResponse(status=200)
    return HttpResponse(status=403)


@CorsHttpDecorator
def getOppCostSettings(request):
    try:
        iSession = request.session['interactives']['opportunity_cost']
        settingObj = OppCostSettings.getorCreateSettings(
                                class_id=iSession.resource_id)
    except:
        return HttpResponse(status=401)
    return HttpResponse(settingObj.settings, 'application/json')


@csrf_exempt
@CorsHttpDecorator
def saveOppCostSettings(request):
    try:
        iSession = request.session['interactives']['opportunity_cost']
        param = iSession.getLaunchParam()
        roles = param['roles']
        if 'Educator' not in roles:
            raise Exception
    except:
        return HttpResponse(status=401)
    rawData = request.body
    newSettings = json.loads(rawData)
    settingsObj = OppCostSettings.getorCreateSettings(class_id=iSession.resource_id)
    settingsObj.settings = json.dumps(newSettings)
    settingsObj.save()
    return HttpResponse(status=200)


@CorsHttpDecorator
def getStudents(request):
    try:
        iSession = request.session['interactives']['opportunity_cost']
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if 'Educator' not in launchParam['roles']:
        return HttpResponse('{}', status=401)
    sessions = InteractiveSession.objects.filter(
                                context_id=iSession.context_id,
                                target_app=iSession.target_app,
                                resource_id=iSession.resource_id)
    students = []
    for s in sessions:
        param = s.getLaunchParam()
        if 'Learner' in s.getLaunchParam()['roles']:
            studentEntry = {
                            'user_id': s.user_id,
                            'name': param['custom_firstname'] + ' ' + param['custom_lastname'],
                            'course_id': s.context_id,
                            'resource_id': iSession.resource_id
                            }
            if iSession.user_id == s.user_id:
                studentEntry['currentStudent'] = True
            students.append(studentEntry)
    students = sorted(students, key=lambda k: k['name'])
    return HttpResponse(json.dumps({'students': students}))


@CorsHttpDecorator
def getStudentData(request):
    try:
        iSession = request.session['interactives']['opportunity_cost']
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if 'Educator' not in launchParam['roles']:
        return HttpResponse('{}', status=401)
    user_id = request.GET['user_id']
    jsonData = InteractiveState.getStudentData(iSession, user_id)
    return HttpResponse(json.dumps(jsonData), 'application/json')


@CorsHttpDecorator
def getAggregates(request):
    try:
        iSession = request.session['interactives']['opportunity_cost']
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if 'Educator' not in launchParam['roles']:
        return HttpResponse('{}', status=401)
    jsonData = InteractiveState.getAllAggregates(iSession)
    return HttpResponse(json.dumps(jsonData), 'application/json')


# make it a class method
@CorsHttpDecorator
def check_for_active_users(request):
    if not request.method == 'GET':
        return HttpResponse(status=401)
    try:
        iSession = request.session['interactives']['opportunity_cost']
    except:
        return HttpResponse(status=401)
    interactive_state_count = InteractiveState.objects.filter(
                                iSession__resource_id=iSession.resource_id,
                                iSession__target_app=iSession.target_app
                                ).count()
    if interactive_state_count > 0:
        return HttpResponse(status=400)
    else:
        return HttpResponse(status=200)
