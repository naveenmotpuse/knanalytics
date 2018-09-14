# Create your views here.
#import os
import json
import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from gldata.models import SessionData
from knanalytics import TPIUtils
import knanalytics.version
from gllaunch.models import InteractiveSession, TPI_Launch_Log

from econ.inflation.models import InflationSettings
import datetime
from econ.monetary_policy.models import FredFFRRate,FredFFTRRate, FredInflationRate,\
    FredMoneySupplyRate, FredRealGDP, FredRealPotentialGDP,\
    FredTotalAssetsHeldRate, FredUERate, FredNaturalUERate

from econ.inflation.models import ConsumerPriceIndex

from econ.common_services.models import FredCrudeOilPrices, FredUSRegConGasPrice

from econ.gdp.models import Fred_ContriesGDPData, Fred_ContriesPOPData, Fred_StatesGDPData, Fred_StatesPOPData, Fred_TotalPOPData
from django.core import serializers
from django.forms.models import model_to_dict
from django.db.models import Count

def CorsHttpResponse(response):
    httpResponse = HttpResponse(response)
    httpResponse['Access-Control-Allow-Origin'] = '*'
    httpResponse['Access-Control-Max-Age'] = '120'
    httpResponse['Access-Control-Allow-Credentials'] = 'true'
    httpResponse['Access-Control-Allow-Methods'] = 'HEAD,GET,OPTIONS,POST,DELETE'
    httpResponse['Access-Control-Allow-Headers'] = 'origin,content-type,accept,x-requested-with'
    return httpResponse


@csrf_exempt
def echo_LTI_vars(request):
    s = "<html><body>"
    s += "<h1>Launch Params as a Dict:</h1>"
    s += "<p>{<br/>"
    # s += "<h1>List of POST request params</h1><ul>"
    for k, v in request.POST.items():
        s += "    &quot;"+k+"&quot;:&quot;"+v+"&quot;,<br/>"
    s += "}</p><br/>"
    s += "</body></html>"
    return CorsHttpResponse(s)

def vb_tool_launch(request):
    response = requests.get("http://api.wantedanalytics.com:7001/wantedapi/v5.0/jobs?passkey=930d854ff36911e480bfa4badbfc9e50&State=Mexico&pagesize=5&pageindex=1", stream=True)
    return response	

@csrf_exempt
def getDupSessions(request):
    try:
        su = request.GET.get('su', "no")
        puser = request.GET.get('u', "")
        presource = request.GET.get('r', "") 
        ptarget = request.GET.get('t', "") 
	if su == "no":
	    sobjects = InteractiveSession.objects.values('user_id','resource_id','target_app').annotate(userCount = Count('user_id')).filter(userCount__gt=1).values_list('user_id', 'resource_id', 'target_app', 'userCount')
            data = []
            for item in sobjects:
                jitem = {}
                jitem["user_id"] = item[0]
                jitem["resource_id"] = item[1]
                jitem["target_app"] = item[2]
                jitem["userCount"] = item[3]
            
                data.append(jitem)
	else:
	    sobjects = InteractiveSession.objects.filter(user_id = puser,resource_id = presource,target_app = ptarget).all()
	    data = []
            for item in sobjects:            
                jitem = {}
                jitem["user_id"] = item.user_id
                jitem["resource_id"] = item.resource_id
                jitem["target_app"] = item.target_app
                jitem["started"] = str(item.started)
                jitem["closed"] = str(item.closed)
                jitem["context_id"] = item.context_id
                jitem["completed"] = str(item.completed)
            
                data.append(jitem)
            
        return HttpResponse(json.dumps(data), status=200)
    except Exception, e:
        return HttpResponse("Error:" + str(e), status=401)

   
@csrf_exempt
def tool_launch(request):
      
    launch_data = {}
    for k, v in request.POST.items():
        launch_data[k] = v
    logTPIRequest(request)
    if TPIUtils.has_valid_signature(launch_data):
        session = SessionData.getOrCreateSession(launch_data)
        return redirect(settings.APP_REDIRECT_URL+'/#/'+session.session_id+'/')
    else:
        return HttpResponse('Unauthorized', status=401)


@csrf_exempt
def force_econ_tool_launch(request):
    return econ_tool_launch(request, False)


@csrf_exempt
def econ_tool_launch(request, check_valid=True):

    launch_data = {}
    trace = ""
    for k, v in request.POST.items():
        launch_data[k] = v       
    
    
    #logTPIRequest(request)
    
    if not check_valid or TPIUtils.has_valid_signature(launch_data,'',request.META['HTTP_REFERER']):
        k_identifier_val = launch_data['custom_target_' + launch_data['custom_currentquestion']]
	
        if (k_identifier_val == 'cpi_inflation' or k_identifier_val == 'monetary_policy' 
            or k_identifier_val == 'opp_cost' or k_identifier_val == 'unemp' or k_identifier_val == 'demand_supply' 
            or k_identifier_val == 'gdp' or k_identifier_val == 'elasticity' or k_identifier_val == 'production_possibilities_frontier'
	    or k_identifier_val == 'gains_from_trade'
            or k_identifier_val.find('qualsims') != -1 or k_identifier_val.find('econ_blair') != -1) :
            k_UpdateFredData(k_identifier_val)
                       
            try:
                pkgPath = ''
                if (k_identifier_val.find('/business/it/') != -1):
                    pkgPath = k_identifier_val
                    pkgPath = pkgPath.replace('-', '_')                
                    pkgPath = '/content/' + pkgPath
                elif (k_identifier_val.find('qualsims') != -1):
                    pkgPath = k_identifier_val
                    #   read LO user config file
                    try:
                        urlorigin = "https://" + request.META.get("HTTP_HOST")                        
                        data = getUserMappings(urlorigin)                           
                    except Exception:
                        #if json file not found then
                        jsonconf = '{"projects": [{"id":"qualsims","users": ["armstrong"]}]}'
                        data = json.loads(jsonconf)
                        
                    #   replace the users 
                    for project in data["projects"]:
                        if (project["id"] == "qualsims"):
                            lousers = project['users']
                            lousers.sort(key = lambda s: len(s), reverse=True)
                            for louser in lousers:
                                pkgPath = rreplace(pkgPath, '/'+louser, '', 1) #pkgPath.replace('/'+louser, '')
                    
                    '''
                    pkgPath = k_identifier_val.replace('/armstrong','').replace('/kotler','').replace('/solomon','')
                    pkgPath = pkgPath.replace('/ebert','').replace('/bovee','')
                    pkgPath = pkgPath.replace('/certo','').replace('/robbins10 Simulation','').replace('/robbins10','').replace('/robbins14','').replace('/robbins17','').replace('/wheelen','')
                    pkgPath = pkgPath.replace('/david','').replace('/barringer','').replace('/dressler','').replace('/mariotti','').replace('/scarborough','')
                    pkgPath = pkgPath.replace('/cheeseman','').replace('/robbins8e', '').replace('/gibson10e', '').replace('/armstrong7e', '')
                    '''
                    
                    pkgPath = pkgPath.replace('-', '_')                
                    pkgPath = '/content/' + pkgPath

                
                if(pkgPath != ''):
		    
		    if launch_data['custom_mode'] == 'setup' or (launch_data['custom_mode'] == 'review' and launch_data['roles'] != 'Learner') or (launch_data['custom_mode'] == 'review' and launch_data['roles'] == 'Learner'):
                        pkgPath = '/content/qualsims/commonfiles'

		    if launch_data['custom_mode'] == 'setup':
                        return redirect(pkgPath + '/settings.html?pid=' + k_identifier_val + '&resid=' + launch_data['custom_resource_id'] + '&restitle=' + launch_data['custom_questiontitle_' +
                                                                                                                                                                        launch_data['custom_currentquestion']])
                    elif launch_data['custom_mode'] == 'preview':
                        mediaarry = k_identifier_val.split('/')
                        mediauser=''
                        if len(mediaarry) > 0:
                            mediauser = mediaarry[len(mediaarry)-1]
                            
                        return redirect(pkgPath + '/#/preview/' + mediauser)
                    elif launch_data['custom_mode'] == 'review' and launch_data['roles'] != 'Learner':
                        session = SessionData.getOrCreateSession(launch_data)            
                        return redirect(pkgPath + '/review.html?'+session.session_id)
                    elif launch_data['custom_mode'] == 'review' and launch_data['roles'] == 'Learner':
                        #interactive = InteractiveSession.startInteractiveSession(launch_data)    
                        session = SessionData.getOrCreateSession(launch_data)                                                   
                        return redirect(pkgPath + '/learner_review.html?sid='+session.session_id)                            
                    else:
                        session = SessionData.getOrCreateSession(launch_data)                     
                        #interactive = InteractiveSession.startInteractiveSession(launch_data)                                            
                        return redirect(pkgPath + '/#/' + session.session_id + '/')
                else:    
                    if launch_data['custom_mode'] == 'setup':
                        return redirect('/content/' + k_identifier_val + '/settings.html?pid=' + k_identifier_val + '&resid=' + launch_data['custom_resource_id'])
                    elif launch_data['custom_mode'] == 'preview':
                        return redirect('/content/' + k_identifier_val + '/#/')
                    elif launch_data['custom_mode'] == 'review' and launch_data['roles'] != 'Learner':
                        session = SessionData.getOrCreateSession(launch_data)            
                        return redirect('/content/' + k_identifier_val + '/review.html?'+session.session_id)
                    else:
                        session = SessionData.getOrCreateSession(launch_data)                     
                        interactive = InteractiveSession.startInteractiveSession(launch_data)
                                            
                        return redirect('/content/' + k_identifier_val + '/#/' + session.session_id + '/')        
            except Exception, e:
                response = HttpResponse('Error: 1235no application ' + k_identifier_val + str(e), 404)
                return response
        else:
	    trace =""
            interactive = InteractiveSession.startInteractiveSession(launch_data)
            try:
                if launch_data['custom_mode'] == 'setup':
                    response = handleSettingsRequest(launch_data)
                elif launch_data['custom_mode'] == 'review' and launch_data['roles'] != 'Learner':
                    response = HttpResponseRedirect(settings.COURSE_REVIEW_LAUNCH_TABLE[interactive.target_app])
                else:
                    response = HttpResponseRedirect(settings.ECON_LAUNCH_TABLE[interactive.target_app])
            except:
                response = HttpResponse('Error: no application ' + interactive.target_app, 404)
            if response.status_code != 302:
                return response
	    
	    try:
		try:
                    interactives = request.session['interactives']                
		except:
		    interactives = {}
                sjson = {}
                sjson["user_id"] = interactive.user_id
                sjson["resource_id"] = interactive.resource_id
                sjson["context_id"] = interactive.context_id
                sjson["target_app"] = interactive.target_app
                sjson["launchParam"] = json.loads(interactive.launchParam)
                sjson["started"] = str(interactive.started)                
                #return HttpResponse("naveen" +  json.dumps(sjson), status=401)
                interactives[interactive.target_app] = sjson
		#return HttpResponse("naveen22" +  json.dumps(sjson), status=401)
            except:
                interactives = {}
                interactives[interactive.target_app] = interactive
            request.session['interactives'] = interactives
            return response
    else:
        return HttpResponse('Unauthorized', status=401)
    

def rreplace(s, old, new, occurence = 1):

    if occurence == 0:
        return s

    left, found, right = s.rpartition(old)

    if found == "":
        return right
    else:
        return rreplace(left, old, new, occurence - 1) + new + right
    

def getUserMappings(urlorigin):
    user_mappings = {}
    user_mappings = json.loads('{ "projects": [ { "id": "qualsims", "users": ["armstrong14","dessler16","solomon10","glackin5","tuckwell","wild8e","griffin8e","wild","cheeseman10","barringer6","certo15","moriarty","barney","dessler4","dessler5","scarborough9","scarborough8","martocchio","ebert12","ebert11","robbins14global","armstrong","kotler","solomon","ebert","bovee","certo","robbins10 Simulation","robbins10","robbins14","robbins17","robbins18","wheelen","david","barringer","dressler","mariotti","scarborough","cheeseman","robbins8e","gibson10e","armstrong7e","capstone","pom17global","robbinsmgmt14ge"] } ] }')
    return user_mappings


def oldgetUserMappings(urlorigin):
    user_mappings = {}
    try:            
        r = requests.get(urlorigin + '/content/qualsims/LOusersData.json')
        if r.status_code == 200:
            user_mappings = r.json()	   
        else:    
	    user_mappings = json.loads('{"projects": [{"id": "qualsims","users": ["robbins14global"]}]}')
    except Exception as jsonexc:
	 user_mappings = json.loads('{"projects": [{"id": "qualsims","users": ["robbins14global"]}]}')

    return user_mappings

        
def AgetUserMappings(urlorigin):
    return { "projects": [ { "id": "qualsims", "users": ["robbins14global","armstrong","kotler","solomon","ebert","bovee","certo","robbins10 Simulation","robbins10","robbins14","robbins17","wheelen","david","barringer","dressler","mariotti","scarborough","cheeseman","robbins8e","gibson10e","armstrong7e","capstone","pom17global","robbinsmgmt14ge"] } ] } 


def k_UpdateFredData(k_identifier_val):    
    di_identifier = 'knowdl_' + k_identifier_val
    last_run_date = datetime.datetime.strptime('1980-12-01','%Y-%m-%d')  
    present_date =  datetime.datetime.today();  
    try: 
        if (k_identifier_val == 'cpi_inflation' or k_identifier_val == 'monetary_policy' 
            or k_identifier_val == 'demand_supply' or k_identifier_val == 'gdp') :  
            try:
                settingsObj = InflationSettings.getOrCreateSettings(class_id=di_identifier)          
                last_run_date = datetime.datetime.strptime(settingsObj.settings, '%Y-%m-%d');        
            except ValueError:
                last_run_date = datetime.datetime.strptime('1980-12-01','%Y-%m-%d')  
             
            last_run_date = last_run_date + datetime.timedelta(days = 7)  
            
	    print "last_run_date:" +  str(last_run_date) + " present_date:" + str(present_date)  
            
            if last_run_date < present_date:                 
	    #if True:
		print "inside date condition, getting data after 7 days --" + k_identifier_val
                if k_identifier_val == 'cpi_inflation': 
                    ConsumerPriceIndex.fetchCpiData()  
                elif k_identifier_val == 'monetary_policy':         
                    FredFFRRate.fetchFredData()
                    #12Feb2016 - Changes to fetch Federal Funds Target Rate
                    FredFFTRRate.fetchFredData()
                    FredInflationRate.fetchFredData()
                    FredMoneySupplyRate.fetchFredData()
                    FredRealGDP.fetchFredData()
                    FredRealPotentialGDP.fetchFredData()
                    FredTotalAssetsHeldRate.fetchFredData()
                    FredUERate.fetchFredData()
                    FredNaturalUERate.fetchFredData()  
                elif k_identifier_val == 'demand_supply':
                    FredCrudeOilPrices.fetchFredData()
                    FredUSRegConGasPrice.fetchFredData()
                elif k_identifier_val == 'gdp':
                    kwargs = {}    
                    kwargs.update({'srid': 'all'})
                    kwargs.update({'freq': 'all'})
                    Fred_ContriesGDPData.fetchFredData(**kwargs)
                    Fred_ContriesPOPData.fetchFredData(**kwargs)
                    Fred_StatesGDPData.fetchFredData(**kwargs)  
                    Fred_StatesPOPData.fetchFredData(**kwargs)
                    Fred_TotalPOPData.fetchFredData(**kwargs)                         
            
                settingsObj.settings = present_date.strftime("%Y-%m-%d")
                settingsObj.save()
                
    except ValueError:
        pass


def handleSettingsRequest(launchParam):
    roles = launchParam['roles']
    targetApp = launchParam['custom_target_' + launchParam['custom_currentquestion']]
    if 'Learner' in roles:
        return HttpResponse('Unauthorized', status=401)
    else:
        try:
            return HttpResponseRedirect(settings.ECON_SETTINGS_LAUNCH_TABLE[targetApp])
        except:
            return HttpResponse('Page not found.', status=404)


def logTPIRequest(request):
    logValues = []
    logValues.append('TPI Tool Launch request received:')
    logValues.append("request path : " + request.path)
    for k, v in request.POST.items():
        logValues.append('\t' + k + ':' + v)
    msg = TPI_Launch_Log()
    msg.message = '\n'.join(logValues)
    msg.save()


def getVersion(request):
    return HttpResponse(knanalytics.version.DATA_SERVER_VERSION)











#end of file










