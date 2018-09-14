

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotAllowed
from django.template import Context, Template
from django.template.loader import get_template
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.db import IntegrityError

from gldata.models import SessionData, ProblemDefinition
from knanalytics import TPIUtils
import json

def CorsHttpResponse(response, status=200):
    httpResponse = HttpResponse(response)
    httpResponse['Access-Control-Allow-Origin'] = '*'
    httpResponse['Access-Control-Max-Age'] = '120'
    httpResponse['Access-Control-Allow-Credentials'] = 'true'
    httpResponse['Access-Control-Allow-Methods'] = 'HEAD,GET,OPTIONS,POST,DELETE'
    httpResponse['Access-Control-Allow-Headers'] = 'origin,content-type,accept,x-requested-with'
    httpResponse.status_code = status
    return httpResponse

def handle_options(fn):
    def decorate(*args, **kwargs):
        request = args[0]
        if request.method.lower() == 'options':
            return CorsHttpResponse('OK')
        else:
            return fn(*args, **kwargs)
    return decorate

@handle_options
def get_session_data(request, session_id):
    try:
        session = SessionData.objects.get(session_id=session_id)
    except SessionData.DoesNotExist:
        response = CorsHttpResponse('{"status":"error", "details":"no matching session_id for %s"}' % session_id, 404)
        return response
    
    package = {}
    package['session_id'] = session_id
    package['launch_mode'] = session.launch_mode
    try:
        package['launch_data'] = json.loads(session.launch_data)
    except ValueError:
        response = CorsHttpResponse('{"status":"error", "details":"launch_data is not valid JSON"}', 400)

    try:
        package['session_state'] = json.loads(session.problem_state_data)
    except ValueError:
        response = CorsHttpResponse('{"status":"error", "details":"session_state is not valid JSON"}', 400)
    
    return CorsHttpResponse(json.dumps(package))

@csrf_exempt
@handle_options
def put_session_state_data(request, session_id):
    try:
        session = SessionData.objects.get(session_id=session_id)
    except SessionData.DoesNotExist:
        response = CorsHttpResponse('{"status":"error", "details":"no matching session_id for %s"}' % session_id, 404)
        return response
    
    try:
        json.loads(request.body)
    except ValueError:
        response = CorsHttpResponse('{"status":"error", "details":"session_state is not valid JSON"}', 400)
        return response
    
    session.problem_state_data = request.body
    session.save()
    
    return CorsHttpResponse('OK')
    
@csrf_exempt
@handle_options
def create_problem_definition(request, problem_guid):
    try:
        problem = ProblemDefinition.objects.create(problem_guid=problem_guid)
    except IntegrityError:
        response = CorsHttpResponse('{"status":"error", "details":"problem_guid %s already exists"}' % problem_guid, 400)
        return response
    
@csrf_exempt
@handle_options
def put_problem_definition(request, problem_guid):
    
    ProblemDefinition.objects.get_or_create(problem_guid=problem_guid)
    
    try:
        data = json.loads(request.body)
    except ValueError:
        return CorsHttpResponse('{"status":"error", "details":"Problem data is not valid JSON"}', 400)

    ProblemDefinition.objects.filter(problem_guid=problem_guid).update(problem_data=request.body);

    return CorsHttpResponse('OK', 200)
    
@csrf_exempt
@handle_options
def put_solution(request, problem_guid):
    
    problem, created = ProblemDefinition.objects.get_or_create(problem_guid=problem_guid)
    
    try:
        json.loads(request.body)
    except ValueError:
        return CorsHttpResponse('{"status":"error", "details":"Problem data is not valid JSON"}', 400)

    ProblemDefinition.objects.filter(problem_guid=problem_guid).update(correct_data=request.body);

    return CorsHttpResponse('OK', 200)

@handle_options
def get_problem_definition(request, problem_guid):
    try:
        problem = ProblemDefinition.objects.get(problem_guid=problem_guid)
    except SessionData.DoesNotExist:
        response = CorsHttpResponse('{"status":"error", "details":"no matching problem_guid for %s"}' % problem_guid, 404)
        return response
    
    
    return CorsHttpResponse('{"problem_data":'+problem.problem_data+','
                            '"correct_data":'+problem.correct_data+'}', 200)

@csrf_exempt
@handle_options
def delete_problem_definition(request, problem_guid):
    try:
        problem = ProblemDefinition.objects.get(problem_guid=problem_guid)
    except SessionData.DoesNotExist:
        response = CorsHttpResponse('{"status":"error", "details":"no matching problem_guid for %s"}' % problem_guid, 404)
        return response
    
    problem.delete()
    
    return CorsHttpResponse('OK', 200)

@handle_options
def get_problem_list(request):
    try:
        problems = ProblemDefinition.objects.all()
    except SessionData.DoesNotExist:
        problems = [];

    def problem_data(p):
        try:
            jso = json.loads(p.problem_data)
            jso['guid'] = p.problem_guid
            return jso
        except:
            # Don't die just because one problem is bad
            pass

    return CorsHttpResponse(json.dumps([problem_data(p) for p in problems]))
    
@handle_options
def get_problem(request, problem_guid):
    try:
        problem = ProblemDefinition.objects.get(problem_guid=problem_guid)
    except SessionData.DoesNotExist:
        response = CorsHttpResponse('{"status":"error", "details":"no matching problem_guid for %s"}' % problem_guid, 404)
        return response
    
    return CorsHttpResponse(problem.problem_data)

@csrf_exempt
@handle_options
def put_problem_and_solution(request, problem_guid):
    
    problem, created = ProblemDefinition.objects.get_or_create(problem_guid=problem_guid)

    try:
        data = json.loads(request.body)
    except ValueError:
        return CorsHttpResponse('{"status":"error", "details":"Problem data is not valid JSON"}', 400)

    problem.problem_data = json.dumps(data['problem'])
    problem.correct_data = json.dumps(data['solution'])

    problem.save()

    return CorsHttpResponse('OK', 200)
    
@csrf_exempt
@handle_options
def grade_problem_and_report(request, session_id, problem_guid):
    try:
        session = SessionData.objects.get(session_id=session_id)
        launch_data = json.loads(session.launch_data)
    except SessionData.DoesNotExist:
        response = CorsHttpResponse('{"status":"error", "details":"no matching session_id for %s"}' % session_id, 404)
        return response
    except ValueError:
        response = CorsHttpResponse('{"status":"error", "details":"launch_data is not valid JSON"}', 400)
        return response
    
    k_identifier_val = launch_data['custom_target_' + launch_data['custom_currentquestion']]        
    if (k_identifier_val == 'cpi_inflation' or k_identifier_val == 'monetary_policy' 
        or k_identifier_val == 'opp_cost' or k_identifier_val == 'unemp' or k_identifier_val == 'demand_supply' 
        or k_identifier_val == 'gdp' or k_identifier_val == 'elasticity' or  k_identifier_val == 'production_possibilities_frontier'
	or k_identifier_val == 'gains_from_trade'
        or k_identifier_val.find('qualsims') != -1  or k_identifier_val.find('econ_blair') != -1):
        try:
            student_data = json.loads(request.body)
        except ValueError:
            raise ValueError("student_data is not valid JSON")
    
        answers = student_data['answers']
        duration = int(student_data['duration'])
        nAttempts = int(student_data['nAttempts'])
        
        result = student_data    
        
        if problem_guid == 'usefromsession':
            problem_guid = launch_data['custom_target_' + launch_data['custom_currentquestion']] 
    
        if session.launch_mode == 'do':            
            score = float(student_data['score']) 
            pnum =  int(student_data['problemNumber']) 
            try:
                kresp = TPIUtils.submit_outcome(launch_data, problemNumber=pnum, problem_guid=problem_guid, score=score, duration=duration, submissionCount=nAttempts+1)               
            except Exception as e:
                return CorsHttpResponse(str(e), 400)
            
        return CorsHttpResponse(session.launch_mode + "-----------" + str(kresp) + "------------" + str(result) , 200)
            
    else:
        try:
            problem = ProblemDefinition.objects.get(problem_guid=problem_guid)
        except SessionData.DoesNotExist:
            response = CorsHttpResponse('{"status":"error", "details":"no matching problem_guid for %s"}' % problem_guid, 404)
            return response
    
        try:
            student_data = json.loads(request.body)
        except ValueError:
            raise ValueError("student_data is not valid JSON")
    
        answers = student_data['answers']
        duration = int(student_data['duration'])
        nAttempts = int(student_data['nAttempts'])
    
        try:
            result = problem.grade_response(answers)
        except Exception as e:
            return CorsHttpResponse(str(e), 400)
    
        if session.launch_mode == 'do':
            try:
                pnum, points = session.problem_assignment_info(problem_guid)
            except TypeError:
                return CorsHttpResponse('Points not found for problem guid ' + problem_guid, 400)
    
            score = float(result['score']) * points
    
            TPIUtils.submit_outcome(launch_data, problemNumber=pnum, problem_guid=problem_guid, score=score, duration=duration, submissionCount=nAttempts+1)            
        
        # TODO: test if submission was successful
        return CorsHttpResponse(json.dumps(result), 200)

@csrf_exempt
@handle_options
def grade_problem(request, problem_guid):
    try:
        problem = ProblemDefinition.objects.get(problem_guid=problem_guid)
    except SessionData.DoesNotExist:
        response = CorsHttpResponse('{"status":"error", "details":"no matching problem_guid for %s"}' % problem_guid, 404)
        return response

    student_data = request.body

    try:
        result = problem.grade_response(student_data)
    except Exception as e:
        return CorsHttpResponse(str(e), 400)

    return CorsHttpResponse(json.dumps(result), 200)






#end of file





