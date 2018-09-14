

import collections
import json
import random
from datetime import datetime
import decimal

from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Min, Max

from econ.monetary_policy.models import Indicator, Tool, VARIABLE_CHOICES,\
 MPSettings, Situation, Comment, Vote, Question, Answer
from datacapture.models import InteractiveState, InteractiveLevel
from gllaunch.models import InteractiveSession
from knanalytics import TPIUtils
from econ.utils import CorsHttpDecorator
from collections import defaultdict
from econ.monetary_policy.models import FredFFRRate,FredFFTRRate, FredInflationRate,\
    FredMoneySupplyRate, FredRealGDP, FredRealPotentialGDP,\
    FredTotalAssetsHeldRate, FredUERate, FredNaturalUERate, GraphEvent,\
    Recession


HINT_CHOICES = ['hint_2', 'hint_1']
ECONOMIC_SITUATIONS_1 = ['E1', 'E2', 'C1', 'C2']
ECONOMIC_SITUATIONS_2 = ['A1', 'A2', 'A3']

#12Feb2016 - Changes to fetch Federal Funds Target Rate
FRED_DB_MAP = {'ffr': FredFFRRate,
               'fftr': FredFFTRRate,
               'rgdp': FredRealGDP,
               'gdp': FredRealPotentialGDP,
               'tah': FredTotalAssetsHeldRate,
               'ir': FredInflationRate,
               'ms': FredMoneySupplyRate,
               'ue': FredUERate,
               'nue': FredNaturalUERate,
               }


@CorsHttpDecorator
def getMPState(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['monetary_policy']
        launchParam = iSession.getLaunchParam()
        settingObj = MPSettings.getOrCreateSettings(
                                class_id=launchParam['custom_resource_id']
                                )
    except:
        return HttpResponse(status=401)
    level_settings = json.loads(settingObj.settings)
    fed_settings = json.loads(settingObj.fed_settings)
    levelCount = sum([level_dict['status'] for level_dict in level_settings])
    mp_settings = {'settings': level_settings,
                   'fed_settings': fed_settings,
                   }
    activated_levels = sorted([item['id'] for item in level_settings if item['status']])
    mpState = InteractiveState.getOrCreateInteractiveState(
                                    iSession,
                                    activated_levels=activated_levels,
                                    levelCount=levelCount,
                                    )
    try:
        customData = json.loads(mpState.customData)
    except:
        customData = {}
    history = mpState.getHistory()
    response = {
            'currentLevel': mpState.currentLevel,
            'mode': launchParam['custom_mode'],
            'role': launchParam['roles'],
            'name': {'first': launchParam['custom_firstname'],
                     'last': launchParam['custom_lastname']
                     },
            'customData': customData,
            'attemptsAllowed': float(launchParam['custom_attemptsallowed']),
            'attemptsCompleted': InteractiveLevel.objects.filter(
                        parent__iSession=iSession).count()/mpState.levels,
            'history': history,
            'settings': mp_settings
        }
    request.session['mpHistory'] = history
    return HttpResponse(json.dumps(response),
                        status=200,
                        content_type="application/json"
                        )


@CorsHttpDecorator
def startMPLevel(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['monetary_policy']
    except:
        return HttpResponse(status=401)
    try:
        level = int(request.GET['level'])
    except:
        return HttpResponse(status=400)
    mpState = InteractiveState.objects.get(iSession=iSession, active=True)
    if not mpState.startLevel(level):
        return HttpResponse(status=400)
    return HttpResponse(status=200)


@csrf_exempt
@CorsHttpDecorator
def saveMPLevel(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['monetary_policy']
    except:
        return HttpResponse(status=401)
    history = request.session['mpHistory']
    try:
        params = json.loads(request.body)
        level = params['level']
        score = params['score']
        levelData = json.dumps(params['data'])
    except:
        return HttpResponse(status=400)
    mpState = InteractiveState.objects.get(iSession=iSession, active=True)
    activated_levels = json.loads(mpState.activated_levels)
    bestScore = mpState.saveLevel(level=level, score=score, data=levelData)
    history['attempts'][activated_levels.index(level)] += 1
    if mpState.isComplete() and bestScore:
        TPIUtils.sendTPIReport(mpState, mpState.levels)
    request.session['mpHistory'] = history
    response = {'nextLevel': mpState.currentLevel,
                'savedLevel': level,
                'score': score,
                'retry': mpState.getCurrentOp(),
                'highScore': bestScore,
                'attempts': history['attempts']
                }
    return HttpResponse(json.dumps(response),
                        content_type="application/json",
                        status=200
                        )


@csrf_exempt
@CorsHttpDecorator
def saveMPCustomData(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['monetary_policy']
    except:
        return HttpResponse(status=401)
    mpState = InteractiveState.objects.get(iSession=iSession,
                                           active=True
                                           )
    mpState.customData = request.body
    mpState.save()
    return HttpResponse(status=200)


@CorsHttpDecorator
def getAggregates(request):
    try:
        iSession = request.session['interactives']['monetary_policy']
    except:
        return HttpResponse('{}', status=401)
    launchParam = iSession.getLaunchParam()
    if 'Educator' not in launchParam['roles']:
        return HttpResponse('{}', status=401)
    jsonData = InteractiveState.getAllAggregates(iSession, levelcount=5)
    return HttpResponse(json.dumps(jsonData), 'application/json')


@CorsHttpDecorator
def getStudents(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['monetary_policy']
    except:
        return HttpResponse(status=401)
    launchParam = iSession.getLaunchParam()
    if 'Learner' in launchParam['roles']:
        return HttpResponse(status=401)
    sessions = InteractiveSession.objects.filter(
                                    context_id=iSession.context_id,
                                    target_app=iSession.target_app,
                                    resource_id=iSession.resource_id
                                    )
    students = []
    for s in sessions:
        param = s.getLaunchParam()
        if True:
            studentEntry = {'user_id': s.user_id,
                            'name': param['custom_firstname'] + ' ' + param['custom_lastname'],
                            'course_id': s.context_id,
                            'resource_id': iSession.resource_id
                            }
            if iSession.user_id == s.user_id:
                studentEntry['currentStudent'] = True
            students.append(studentEntry)
    students = sorted(students, key=lambda k: k['name'])
    return HttpResponse(json.dumps({'students': students}),
                        status=200,
                        content_type="application/json"
                        )


@CorsHttpDecorator
def getStudentData(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['monetary_policy']
    except:
        return HttpResponse(status=401)
    launchParam = iSession.getLaunchParam()
    if 'Learner' in launchParam['roles']:
        return HttpResponse(status=401)
    user_id = request.GET['user_id']
    jsonData = InteractiveState.getStudentData(iSession, user_id, levelcount=5)
    return HttpResponse(json.dumps(jsonData), 'application/json')


@CorsHttpDecorator
def get_indicators(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    tool = request.GET.get('tool')
    mode = request.GET.get('mode')
    try:
        tool_object = Tool.objects.get(slug=tool, mode=mode)
    except:
        return HttpResponse(status=400)
    indicators = Indicator.objects.filter(tool=tool_object)
    indicators_dict = collections.defaultdict(dict)
    for variable in VARIABLE_CHOICES:
        indicator_set = indicators.filter(variable=variable[0])
        for item in indicator_set:
            indicators_dict[item.variable].update({item.slug: {'value': item.value,
                                                               'comment': item.comment
                                                               }
                                                   })
    data = {}
    data['title'] = tool_object.name
    data[tool_object.get_mode_display()] = indicators_dict
    return HttpResponse(json.dumps(data), status=200, content_type='application/json')


@csrf_exempt
@CorsHttpDecorator
def check_indicators(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    request_dict = json.loads(request.body)
    tool_name = request_dict.get('tool')
    tool_mode = request_dict.get('mode')
    variable = request_dict.get('variable')
    attempt = request_dict.get('attempt')
    data = request_dict.get('data')
    try:
        tool = Tool.objects.get(slug=tool_name, mode=tool_mode)
        indicator_queryset = Indicator.objects.filter(tool=tool,
                                                      variable=variable
                                                      )
    except:
        return HttpResponse(status=400)
    indicator_dict = collections.defaultdict(dict)
    for indicator in indicator_queryset:
        if indicator.value == data[indicator.slug]:
            indicator_dict[indicator.slug] = {"status": True,
                                              "comment": indicator.comment,
                                              }
        else:
            if attempt:
                indicator_dict[indicator.slug] = {"status": False, }
            else:
                indicator_dict[indicator.slug] = {"status": False,
                                                  "comment": indicator.comment,
                                                  }
    response_dict = {'title': tool.slug,
                     tool.get_mode_display(): {variable: indicator_dict}
                     }
    return HttpResponse(json.dumps(response_dict),
                        status=200,
                        content_type='application/json'
                        )


@CorsHttpDecorator
def getMPSettings(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    try:
        iSession = request.session['interactives']['monetary_policy']
        settingObj = MPSettings.getOrCreateSettings(class_id=iSession.resource_id)
        level_settings = json.loads(settingObj.settings)
        fed_settings = json.loads(settingObj.fed_settings)
        settings = {'settings': level_settings,
                    'fed_settings': fed_settings,
                    }
    except:
        return HttpResponse(status=400)
    return HttpResponse(json.dumps(settings),
                        status=200,
                        content_type='application/json')


@csrf_exempt
@CorsHttpDecorator
def saveMPSettings(request):
    if not request.method == 'POST':
        return HttpResponse(status=401)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    try:
        iSession = request.session['interactives']['monetary_policy']
        param = iSession.getLaunchParam()
        roles = param['roles']
        if 'Learner' in roles:
            raise Exception
    except:
        return HttpResponse(status=401)
    try:
        rawData = json.loads(request.body)
        level_settings = rawData['settings']
        fed_settings = rawData['fed_settings']
    except:
        return HttpResponse(status=400)
    settingObj = MPSettings.objects.get(class_id=iSession.resource_id)
    settingObj.settings = json.dumps(level_settings)
    settingObj.fed_settings = json.dumps(fed_settings)
    settingObj.save()
    return HttpResponse(status=200)


# make it a class method
@CorsHttpDecorator
def check_for_active_users(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['monetary_policy']
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


@CorsHttpDecorator
def restart(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
    try:
        iSession = request.session['interactives']['monetary_policy']
    except:
        return HttpResponse(status=400)
    if InteractiveState.restart(iSession=iSession):
        return HttpResponse(status=200)
    return HttpResponse(status=403)


@CorsHttpDecorator
def get_economic_situation(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    shuffle_id = int(request.GET.get('shuffle_id'))
    situation_slug = request.GET.get('slug')
    if not situation_slug:
        if not shuffle_id:
            situation_slug = random.choice(ECONOMIC_SITUATIONS_1)
        else:
            situation_slug = random.choice(ECONOMIC_SITUATIONS_2)
    try:
        situation_object = Situation.objects.get(slug=situation_slug)
    except:
        return HttpResponse(status=400)
    response_dict = defaultdict(dict)
    response_dict.update({'situation': situation_slug,
                          'overview': json.loads(situation_object.overview),
                          'fomc_data': json.loads(situation_object.fomc_data),
                          'policy_summary': json.loads(situation_object.policy_summary),
                          'intended_effects': json.loads(situation_object.intended_effects)})
    comment_options = [{'comment_id': comment.id,
                        'comment_text': str(comment.comment_text)
                        } for comment in Comment.objects.filter(situation=situation_object)]
    vote_options = [{'vote_id': vote.id,
                     'vote_text': str(vote.vote_text)
                     } for vote in Vote.objects.filter(situation=situation_object)]
    response_dict.update({'student_data': {'comment_options': comment_options,
                                           'vote_options': vote_options
                                           }
                          })
    return HttpResponse(json.dumps(response_dict), status=200, content_type='application/json')


@CorsHttpDecorator
def get_question(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    question_id = request.GET.get('question_id')
    optional_id = request.GET.get('optional_id')
    if optional_id:
        try:
            question = Question.objects.get(id=optional_id)
        except:
            return HttpResponse(status=400)
    else:
        try:
            question = Question.objects.get(question_text__contains="Question %s" % question_id)
        except:
            try:
                question_list = Question.objects.filter(question_text__contains="Question %s" % question_id)
                question = random.choice(question_list)
            except:
                return HttpResponse(status=400)
    response_dict = {}
    response_dict.update({'questionID': question.id,
                          'question': question.question_text,
                          'multi_choice': question.multi_choice,
                          'weight': question.weight,
                          'max_attempts': question.max_attempts
                          })
    if question.extra_data:
        response_dict.update(json.loads(question.extra_data))
    if not question.multi_choice:
        options = [{'optionID': option.id,
                    'option': option.answer_text
                    } for option in question.answer_set.all()]
        random.shuffle(options)
    else:
        options = question.get_multi_options()
    response_dict.update({'options': options})
    return HttpResponse(json.dumps(response_dict),
                        content_type='application/json',
                        status=200)


@csrf_exempt
@CorsHttpDecorator
def check_answer(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    request_dict = json.loads(request.body)
    option_id = request_dict.get('option_id')
    if isinstance(option_id, list):
        multiple_choice = True
    else:
        multiple_choice = False
    r_attempts = request_dict.get('r_attempts')
    try:
        if multiple_choice:
            options = Answer.objects.filter(id__in=option_id)
            option = Answer()
            option.question = Question.objects.get(id=options[0].question_id)
            option.status = reduce(lambda x, y: x and y,
                                   [option.status for option in options])
            if option.status:
                option.feedback = "Correct"
            else:
                option.feedback = None
        else:
            option = Answer.objects.get(id=option_id)
    except:
        return HttpResponse(status=400)
    response_dict = {}
    response_dict.update({'status': option.status})
    if option.status:
        feedback = option.feedback
    else:
        if option.feedback:
            feedback = json.loads(option.feedback)[r_attempts]
        else:
            feedback = json.loads(option.question.feedback)[r_attempts]
    if not r_attempts and not option.status:
        if not multiple_choice:
            correct_answer = Answer.objects.get(question=option.question,
                                                status=True
                                                )
            answer_id = correct_answer.id
        else:
            correct_answer = Answer.objects.filter(question=option.question,
                                                   status=True)
            answer_id = [answer.id for answer in correct_answer]
        response_dict.update({
                              'answer_id': answer_id
                            })
    response_dict.update({'feedback': feedback})
    return HttpResponse(json.dumps(response_dict),
                        content_type='application/json',
                        status=200)


@csrf_exempt
@CorsHttpDecorator
def check_l3_context(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    request_dict = json.loads(request.body)
    context_id = request_dict.get('context_id')
    context = request_dict.get('context')
    persona = request_dict.get('persona')
    response_dict = {}
    try:
        if context == 'comment':
            context_object = Comment.objects.get(id=context_id)
        else:
            context_object = Vote.objects.get(id=context_id)
            x_count = context_object.situation.x_count
            y_count = context_object.situation.y_count
            if context_object.policy_vote:
                x_count += 1
                policy_vote = context_object
            else:
                y_count += 1
                policy_vote = context_object.situation.vote_set.get(
                                                    policy_vote=True
                                                    )
            response_dict.update({'x': x_count,
                                  'y': y_count,
                                  'policy_vote': policy_vote.vote_text.lower(),
                                  'value': policy_vote.value
                                  })
    except:
        return HttpResponse(status=400)
    response_dict.update({'status': context_object.status})
    if persona:
        try:
            feedback = json.loads(context_object.feedback)[persona]
        except:
            return HttpResponse(status=400)
    else:
        feedback = context_object.feedback
    if context_object.situation.slug in ECONOMIC_SITUATIONS_1:
        r_attempts = request_dict.get('r_attempts')
        if not r_attempts:
            if context == "comment":
                response_dict.update({
                    'correct_ids': [int(x) for x in context_object.situation.comment_set.values_list('id', flat=True).filter(status=True)]
                    })
            else:
                response_dict.update({
                    'correct_ids': [int(x) for x in context_object.situation.vote_set.values_list('id', flat=True).filter(status=True)]
                    })
    response_dict.update({'feedback': feedback})
    return HttpResponse(json.dumps(response_dict),
                        content_type='application/json',
                        status=200)


@CorsHttpDecorator
def getFredData(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    try:
        fred_tool_name = request.GET['fred_tool_name']
    except:
        return HttpResponse(status=400)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    kwargs = {}
    if start_date:
        kwargs.update({'start_date': start_date})
    if end_date:
        kwargs.update({'end_date': end_date})
    model_class = FRED_DB_MAP[fred_tool_name]
    try:
        results = model_class.getFredData(**kwargs)
    except:
        return HttpResponse(status=400)
    response = [[result[0].isoformat(), float(result[1])] for result in results]
    return HttpResponse(json.dumps(response),
                        status=200, content_type="application/json")


@csrf_exempt
@CorsHttpDecorator
def check_level4_context(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    try:
        question = Question.objects.get(question_text__contains="Question 4.3")
    except:
        return HttpResponse(status=400)
    request_dict = json.loads(request.body)
    answer_list = request_dict.get('answer_list')
    r_attempts = request_dict.get('r_attempts')
    min_inflation_object = FredInflationRate.objects.filter(
                    observation_value=FredInflationRate.objects.aggregate(
                                        Min('observation_value')
                                        )['observation_value__min']
                                    )[0]
    max_inflation_object = FredInflationRate.objects.filter(
                    observation_value=FredInflationRate.objects.aggregate(
                                        Max('observation_value')
                                        )['observation_value__max']
                                    )[0]
    min_object = FredFFRRate.objects.get(observation_date=min_inflation_object.observation_date)
    max_object = FredFFRRate.objects.get(observation_date=max_inflation_object.observation_date)
    fred_values_list = [
        datetime.strftime(max_object.observation_date, "%Y-%m"),
        str(max_object.observation_value.quantize(decimal.Decimal(10) ** -2)),
        datetime.strftime(min_object.observation_date, "%Y-%m"),
        str(min_object.observation_value.quantize(decimal.Decimal(10) ** -2)),
        ]
    response_dict = {}
    feedback_list = json.loads(question.feedback)
    if answer_list == fred_values_list:
        response_dict.update({
                              'feedback': 'Correct',
                              'status': True
                              })
    else:
        if r_attempts:
            feedback = feedback_list[r_attempts]
        else:
            feedback = feedback_list[r_attempts] % tuple(fred_values_list)
            response_dict.update({'answer_id': fred_values_list})
        response_dict.update({
                              'feedback': feedback,
                              'status': False
                              })
    return HttpResponse(json.dumps(response_dict),
                        status=200,
                        content_type="application/json"
                        )


@CorsHttpDecorator
def getGraphEvents(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    kwargs = {}
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    if start_date:
        kwargs.update({'start_date': start_date})
    if end_date:
        kwargs.update({'end_date': end_date})
    try:
        graph_events = GraphEvent.get_graph_events(**kwargs)
    except:
        return HttpResponse(status=400)
    response_list = []
    for item in graph_events:
        response_list.append({"event_date": item.event_date.isoformat(),
                              "event_description": item.event_description,
                              })
    return HttpResponse(json.dumps(response_list),
                        status=200,
                        content_type="application/json"
                        )


@CorsHttpDecorator
def getRecessionPeriods(request):
    if not request.method == 'GET':
        return HttpResponse(status=400)
#     try:
#         request.session['interactives']['monetary_policy']
#     except:
#         return HttpResponse(status=401)
    kwargs = {}
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    if start_date:
        kwargs.update({'start_date': start_date})
    if end_date:
        kwargs.update({'end_date': end_date})
    try:
        recession_periods = Recession.get_recession_periods(**kwargs)
    except:
        return HttpResponse(status=400)
    response_list = []
    for item in recession_periods:
        response_list.append({"start_date": item.start_date.isoformat(),
                              "end_date": item.end_date.isoformat()
                              })
    return HttpResponse(json.dumps(response_list),
                        status=200,
                        content_type="application/json"
                        )
                        
                        
                        
                        




