









from datetime import datetime
import json

from django.conf import settings
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from gldata.models import SessionData
from datacapture.models import InteractiveState, InteractiveLevel
from econ.inflation.models import ConsumerPriceIndex
from econ.utils import CorsHttpDecorator
from gllaunch.models import InteractiveSession
from knanalytics import TPIUtils
from econ.inflation.models import InflationSettings



@CorsHttpDecorator
def getInflationState(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['inflation']
        launchParam = iSession.getLaunchParam()
        settingsObj = InflationSettings.getOrCreateSettings(
                            class_id=launchParam['custom_resource_id'])
    except:
        return HttpResponse(status=401)
    level_settings = json.loads(settingsObj.settings)
    levelCount = sum(level_settings.values())
    activated_levels = get_activated_levels(level_settings)
    inflation = InteractiveState.getOrCreateInteractiveState(
                                            iSession,
                                            activated_levels=activated_levels,
                                            levelCount=levelCount
                                            )
    levels = InteractiveLevel.objects.filter(parent=inflation,
                                             completed=True).order_by('level')
    levelData = {}
    scores = [0, 0, 0, 0, 0, 0]
    for i in activated_levels:
        for l in levels:
            if l.level == i:
                scores[i] = l.score
                levelData['level%d' % i] = l.levelData
                break
        try:
            levelData['level%d' % i]
        except:
            levelData['level%d' % i] = ''
    history = inflation.getHistory()
    response = {
                'currentLevel': inflation.currentLevel,
                'mode': launchParam['custom_mode'],
                'name': {'first': launchParam['custom_firstname'],
                         'last': launchParam['custom_lastname']
                         },
                'data': levelData,
                'customData': inflation.customData,
                'attemptsAllowed': float(
                            launchParam['custom_attemptsallowed']),
                'attemptsCompleted': levels.count()/inflation.levels,
                'scores': scores,
                'settings': level_settings,
                'history': history
                }
    request.session['inflationHistory'] = history
    return HttpResponse(json.dumps(response),
                        status=200,
                        content_type='application/json'
                        )


@CorsHttpDecorator
def startInflationLevel(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['inflation']
    except:
        return HttpResponse(status=401)
    try:
        level = int(request.GET['level'])
    except:
        return HttpResponse(status=400)
    inflation = InteractiveState.objects.get(iSession=iSession,
                                             active=True)
    if not inflation.startLevel(level):
        return HttpResponse(status=400)
    return HttpResponse(status=200)


@csrf_exempt
@CorsHttpDecorator
def saveInflationLevel(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['inflation']
    except:
        return HttpResponse(status=401)
    history = request.session['inflationHistory']
    try:
        params = json.loads(request.body)
        level = params['level']
        score = params['score']
        levelData = json.dumps(params['data'])
    except:
        return HttpResponse(status=400)
    inflationState = InteractiveState.objects.get(iSession=iSession, active=True)
    activated_levels = json.loads(inflationState.activated_levels)
    bestScore = inflationState.saveLevel(level=level, score=score, data=levelData)
    history['attempts'][activated_levels.index(level)] += 1
    if inflationState.isComplete() and bestScore:
        TPIUtils.sendTPIReport(inflationState, inflationState.levels)
    resp = {'nextLevel': inflationState.currentLevel,
            'savedLevel': level,
            'score': score,
            'retry': inflationState.getCurrentOp(),
            'highScore': bestScore,
            'attempts': history['attempts']
            }
    return HttpResponse(json.dumps(resp),
                        status=200,
                        content_type='application/json'
                        )


@csrf_exempt
@CorsHttpDecorator
def saveInflationCustomData(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['inflation']
    except:
        return HttpResponse(status=401)
    inflationState = InteractiveState.objects.get(iSession=iSession, active=True)
    inflationState.customData = request.body
    inflationState.save()
    return HttpResponse(status=200)


@csrf_exempt
@CorsHttpDecorator
def restart(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['inflation']
    except:
        return HttpResponse(status=401)
    if InteractiveState.restart(iSession=iSession):
        return HttpResponse(status=200)


@CorsHttpDecorator
def getCpiData(request, index_names):
    if index_names != 'all':
        index_names = index_names.split(',')
    else:
        index_names = []
    if 'start_date' in request.GET:
        start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d')
    else:
        start_date = None
    if 'end_date' in request.GET:
        end_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d')
    else:
        end_date = None
    try:
        data = ConsumerPriceIndex.getCpiData(index_names, start_date, end_date)
    except Exception, e:
        return HttpResponse('{}'+ str(e), status=500)
    return HttpResponse(json.dumps(data),
                        status=200,
                        content_type='application/json'
                        )


# make it a class method

@csrf_exempt
@CorsHttpDecorator
def check_for_active_users(request):
    knowdlresourceid = ''
    knowdltargetapp = ''
    try:
        knowdldata = json.loads(request.body)
        if 'knowdlresourceid' in knowdldata:
            knowdlresourceid = knowdldata['knowdlresourceid']
            knowdltargetapp = knowdldata['knowdltargetapp']
        else:
            knowdlresourceid = ''
            knowdltargetapp =''
    except ValueError:        
        pass
    
    if knowdlresourceid != '':
        interactive_session_count = InteractiveSession.objects.filter(
                                      target_app=knowdltargetapp, 
                                      resource_id=knowdlresourceid
                                      ).count()
        
        return HttpResponse(json.dumps(interactive_session_count),
                        status=200,
                        content_type='application/json'
                        )
    else:    
        if not request.method == 'GET':
            return HttpResponse(status=401)
        try:
            iSession = request.session['interactives']['inflation']
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


@csrf_exempt
@CorsHttpDecorator
def getInflationSettings(request):
    knowdlresourceid = ''
    knowdltargetapp = ''
    try:
        knowdldata = json.loads(request.body)
        if 'knowdlresourceid' in knowdldata:
            knowdlresourceid = knowdldata['knowdlresourceid']
            knowdltargetapp = knowdldata['knowdltargetapp']
        else:
            knowdlresourceid = ''
            knowdltargetapp =''
    except ValueError:        
        pass
    
    if knowdlresourceid != '':
        try:  
            try:  
                settingsoldObj =  InflationSettings.objects.get(
                                        class_id=knowdlresourceid) 
                if settingsoldObj != None:
                    settingsoldObj.class_id=knowdlresourceid + '_' + knowdltargetapp                
                    settingsoldObj.save()
            except:
                pass       
            settingsObj = InflationSettings.getOrCreateSettings(
                                    class_id=knowdlresourceid + '_' + knowdltargetapp)
            settings = json.loads(settingsObj.settings)
        except:
            HttpResponse(status=400)
            
        return HttpResponse(json.dumps(settings),
                            status=200,
                            content_type='application/json'
                            )
    else:
        if not request.method == 'GET':
            return HttpResponse(status=400)
        try:
            iSession = request.session['interactives']['inflation']
            settingsObj = InflationSettings.getOrCreateSettings(
                                class_id=iSession.resource_id)
            settings = json.loads(settingsObj.settings)
        except:
            HttpResponse(status=400)
        return HttpResponse(json.dumps(settings),
                            status=200,
                            content_type='application/json'
                            )


@csrf_exempt
@CorsHttpDecorator
def saveInflationSettings(request):
    knowdlresourceid = ''
    knowdltargetapp = ''
    try:
        knowdldata = json.loads(request.body)
        if 'knowdlresourceid' in knowdldata:
            knowdlresourceid = knowdldata['knowdlresourceid']
            knowdltargetapp = knowdldata['knowdltargetapp']            
            level_settings = knowdldata['settings']
        else:
            knowdlresourceid = ''
            knowdltargetapp =''
    except ValueError:
        pass    
    
    if knowdlresourceid != '':
        try:        
            settingsObj = InflationSettings.objects.get(
                                    class_id=knowdlresourceid + '_' + knowdltargetapp)
            settingsObj.settings = json.dumps(level_settings)
            settingsObj.save()
            return HttpResponse(status=200)
        except:
            HttpResponse(status=400)        
    else:
        if not request.method == 'POST':
            return HttpResponse(status=401)
        try:
            iSession = request.session['interactives']['inflation']
            param = iSession.getLaunchParam()
            roles = param['roles']
            if 'Learner' in roles:
                raise Exception
        except:
            return HttpResponse(status=401)
        try:
            level_settings = json.loads(request.body)
        except:
            return HttpResponse(status=400)
        settingsObj = InflationSettings.objects.get(
                                    class_id=iSession.resource_id)
        settingsObj.settings = json.dumps(level_settings)
        settingsObj.save()
        return HttpResponse(status=200)


def getAggregates(request):
    try:
        iSession = request.session['interactives']['inflation']
    except:
        return HttpResponse(status=401)
    launchParam = iSession.getLaunchParam()
    if 'Educator' not in launchParam['roles']:
        return HttpResponse(status=401)
    jsonData = InteractiveState.getAllAggregates(iSession, levelcount=6)
    return HttpResponse(json.dumps(jsonData),
                        status=200,
                        content_type='application/json'
                        )


@csrf_exempt
@CorsHttpDecorator
def getStudents(request):
    knowdlresourceid = ''
    knowdltargetapp = ''
    knowdlcontextid = ''
    try:
        knowdldata = json.loads(request.body)
        if 'knowdlresourceid' in knowdldata:
            knowdlresourceid = knowdldata['knowdlresourceid']
            knowdltargetapp = knowdldata['knowdltargetapp']
            knowdlcontextid = knowdldata['knowdlcontextid']
        else:
            knowdlresourceid = ''
            knowdltargetapp =''
            knowdlcontextid = ''
    except ValueError:        
        pass
    
    if knowdlresourceid != '': 
        if 'Educator' not in knowdldata['roles']:
            return HttpResponse(status=401)
        
        sessions = InteractiveSession.objects.filter(
                                    context_id=knowdlcontextid,
                                    target_app=knowdltargetapp,
                                    resource_id=knowdlresourceid)
        students = []
        for s in sessions:            
            lparam = s.getLaunchParam()
            session_id = SessionData.constructSessionID(lparam)
            newsession_id = session_id +'_'+ knowdltargetapp
            try:                
                oldsession = SessionData.objects.get(session_id=session_id)
                if oldsession != None and oldsession.session_id != None and oldsession.session_id != '':                
                    oldsession.session_id = newsession_id
                    oldsession.save()
                    session_id = newsession_id
            except SessionData.DoesNotExist:
                session_id = newsession_id
                pass
                
            if 'Learner' in lparam['roles']:
                studentEntry = {
                                'user_id': s.user_id,
                                'name': "%s %s" % (lparam['custom_firstname'], lparam['custom_lastname']),
                                'course_id': s.context_id,
                                'resource_id': knowdlresourceid,
                                'session_id':session_id                                
                                }                
                students.append(studentEntry)
                
        students = sorted(students, key=lambda k: k['name'])
        return HttpResponse(json.dumps({'students': students}))
    else:
        try:
            iSession = request.session['interactives']['inflation']
        except:
            return HttpResponse(status=401)
        launchParam = iSession.getLaunchParam()
        if 'Educator' not in launchParam['roles']:
            return HttpResponse(status=401)
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
                                'name': "%s %s" % (param['custom_firstname'], param['custom_lastname']),
                                'course_id': s.context_id,
                                'resource_id': iSession.resource_id
                                }
                if iSession.user_id == s.user_id:
                    studentEntry['currentStudent'] = True
                students.append(studentEntry)
        students = sorted(students, key=lambda k: k['name'])
        return HttpResponse(json.dumps({'students': students}))


def getStudentData(request):
    try:
        iSession = request.session['interactives']['inflation']
    except:
        return HttpResponse(status=401)
    launchParam = iSession.getLaunchParam()
    if 'Educator' not in launchParam['roles']:
        return HttpResponse(status=401)
    user_id = request.GET['user_id']
    jsonData = InteractiveState.getStudentData(iSession, user_id, levelcount=6)
    return HttpResponse(json.dumps(jsonData),
                        status=200,
                        content_type='application/json'
                        )


def get_activated_levels(level_settings):
    activated_levels = []
    if level_settings.get('intro'):
        activated_levels.append(0)
    activated_levels.extend([int(level[0].split('level')[1]) for level in level_settings.items() if level[1] and level[0] != 'intro'])
    return sorted(activated_levels)



#end of file











