from django.shortcuts import render

# Create your views here.

import json
import requests
import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from knowdlsim.models import RevelAssignments, RevelSettings,RevelAssignmentDetails \
    , RevelMasterAttemptData, RevelMasterQuestions, RevelQuestionAttemptDetails

from knowdlsim import jwtValidator
from knowdlsim.jwtValidator import validateToken
from decimal import Decimal

from django.db.models import Max

def CorsHttpResponse(response, status=200):
    httpResponse = HttpResponse(response)
    httpResponse['Access-Control-Allow-Origin'] = '*'
    httpResponse['Access-Control-Max-Age'] = '120'
    httpResponse['Access-Control-Allow-Credentials'] = 'true'
    httpResponse['Access-Control-Allow-Methods'] = 'HEAD,GET,OPTIONS,POST,DELETE'
    httpResponse['Access-Control-Allow-Headers'] = 'origin,content-type,accept,x-requested-with'
    httpResponse.status_code = status
    return httpResponse

def getTemplateMappings(urlorigin):
    template_mappings = {}         
    try:            
        r = requests.get(urlorigin + '/content/revelsims/commonfiles/template_mappings.json')
        if r.status_code == 200:
            template_mappings = r.json()
        else:    
            template_mappings = json.loads('{"TemplateId": "ModulePath", "JWKS_URL": "https://int-piapi.stg-openclass.com/v1/piapi-int/tokens/jwks.json", "common_files":"/revelsims/commonfiles/", "38a1192c-778f-11e7-b5a5-be2e44b06b34":"/revelsims/sim1/", "03cfb0f7-9aab-4cf4-892a-e8f02abea6f7":"/revelsims/CJ001/"}')
    except Exception as jsonexc:
        template_mappings = json.loads('{"TemplateId": "ModulePath", "JWKS_URL": "https://int-piapi.stg-openclass.com/v1/piapi-int/tokens/jwks.json", "common_files":"/revelsims/commonfiles/", "38a1192c-778f-11e7-b5a5-be2e44b06b34":"/revelsims/sim1/", "03cfb0f7-9aab-4cf4-892a-e8f02abea6f7":"/revelsims/CJ001/"}')
        
    return template_mappings 
         
    

#http://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/launch/{courseid}/{assignmentid}/
@csrf_exempt
def k_launch(request,course_id,assignment_id=""):
    trace = ""
    refererurl = ""
    urlorigin = "https://revel-ilp.knowdl.com"
    try:        
        try:
            
            #RevelAssignments.SaveReqMetaData(request.META, "Launch")
            #RevelAssignments.SaveReqMetaData(request.body, "Launch")
            refererurl = request.META['HTTP_REFERER'] 
            urlorigin = "https://" + request.META.get("HTTP_HOST")
        except Exception as rqEx:
            trace = trace + str(rqEx)
        trace = trace + "urlorigin" + urlorigin + "--refererurl:" + refererurl
        t_mapper = getTemplateMappings(urlorigin)
        trace = trace + str(t_mapper)   
        if assignment_id != "": 
            noduedc = 0
            try: 
                noduedc = RevelAssignmentDetails.objects.filter(assignmentId=assignment_id,courseId=course_id, additionalField3 = "NoDueDate").count()
            except Exception as myex:
                noduedc = 0
                      
            retObj = RevelAssignments.GetAssignment(course_id, assignment_id)
	    trace = trace + " getassignment()"
            templateId = retObj['templateId']
            modulepath = urlorigin + t_mapper[templateId]        
            #modulepath = urlorigin + "/revelsims/marketing-mix/"
	    activityId = retObj['activities'][0]['activityId'] 
            custMode = 'do'        
            try:   
                custMode = request.GET.get('custom_mode', 'do')
            except Exception, innex:
                custMode = 'do'
                
            if custMode == "do" or custMode == "preview":            
                return redirect(modulepath + "index.htm?courId=" + course_id + "&assiId=" + assignment_id + "&tempId=" + templateId + "&actiId=" + activityId + "&mode=" + custMode + "&refurl=" + refererurl)
            else:
                commFilePath = urlorigin  + t_mapper['common_files']  
                #commFilePath = urlorigin + "/revelsims/commonfiles/"
		if custMode == "grade":            
                    return redirect(commFilePath + "instr_review.html?courId=" + course_id + "&assiId=" + assignment_id + "&tempId=" + templateId + "&assiTttle=" + retObj['title'] + "&refurl=" + refererurl)
                elif custMode == "edit": 
                    if noduedc>0:                      
                        return redirect(commFilePath + "settings.html?courId=" + course_id + "&assiId=" + assignment_id + "&tempId=" + templateId + "&assiTttle=" + retObj['title'] + "&NoAsgnId=true" + "&refurl=" + refererurl)
                    else:                                       
                        return redirect(commFilePath + "settings.html?courId=" + course_id + "&assiId=" + assignment_id + "&tempId=" + templateId + "&assiTttle=" + retObj['title'] + "&refurl=" + refererurl)
                    
                elif custMode == "review":
                    return redirect(commFilePath + "learner_review.html?courId=" + course_id + "&assiId=" + assignment_id + "&tempId=" + templateId + "&assiTttle=" + retObj['title'] + "&refurl=" + refererurl)
        else:
            return redirect("/knowdl_revel_sim/commonfiles/error.html?courId=" + course_id + "&assiId=" + assignment_id + "&mode=" + custMode + "&refurl=" + refererurl)
        
    except Exception, e:
        errorpkg = {} 
 	errorpkg['trace'] = trace    
        errorpkg['msg'] = "Error in launch assignment."
        errorpkg['errorobj'] = str(e)  
        errorpkg['assignment_id'] = assignment_id
        errorpkg['course_id'] = course_id      
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")


#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/get/{courseid}/{assignmentid}/
@csrf_exempt
def k_get(request,course_id,assignment_id):    
    try:
        #token = request.META['HTTP_X_AUTHORIZATION'] 
        #urlorigin = "https://" + request.META.get("HTTP_HOST")          
        #t_mapper = getTemplateMappings(urlorigin)    
        #k_payload = validateToken(token,t_mapper['JWKS_URL'])
        
	#if k_payload.get('payload_decoded_and_verified'):                    
        if True:
            retObj = RevelAssignments.GetAssignment(course_id, assignment_id)  
            return HttpResponse(json.dumps(retObj),
                        status=200, content_type="application/json")
        else:
            return HttpResponse(status=403)
            
    except Exception, e:  
        errorpkg = {}      
        errorpkg['msg'] = "Error in create assignment."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")

#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/getall/{courseid}/
#for knowdl use
@csrf_exempt
def k_getAll(request,course_id):    
    try:        
        retObj = {}
        retObj['assignments'] = RevelAssignments.GetAllAssignment(course_id)        
        return HttpResponse(json.dumps(retObj),
                        status=200, content_type="application/json")
    except Exception, e:        
        errorpkg = {}      
        errorpkg['msg'] = "Error in get all assignments. Course Id: " + course_id 
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")
        
#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/getheaders/
#knowdl use
@csrf_exempt
def k_getHeaders(request):    
    try:
        retObj = {}
        retObj['assignments'] = RevelAssignments.GetReqMetaData()        
        return HttpResponse(json.dumps(retObj),
                        status=200, content_type="application/json")
    except Exception, e:        
        errorpkg = {}      
        errorpkg['msg'] = "Error in get metadata assignments."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")


#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/delete/{courseid}/{assignmentid}/
@csrf_exempt
def k_delete(request,course_id,assignment_id):    
    try:  
        token = request.META['HTTP_X_AUTHORIZATION']  
        urlorigin = "https://" + request.META.get("HTTP_HOST")          
        t_mapper = getTemplateMappings(urlorigin)    
        k_payload = validateToken(token,t_mapper['JWKS_URL'])
        if k_payload.get('payload_decoded_and_verified'):                    
            RevelAssignments.DeleteAssignment(course_id, assignment_id)
            return HttpResponse(status=200) 
        else:
            return HttpResponse(status=403)
          
    except Exception, e:
        errorpkg = {}        
        errorpkg['msg'] = "Error in delete assignment."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")
        
#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/deleteall/{courseid}/
@csrf_exempt
def k_deleteAll(request,course_id):    
    try:                   
        RevelAssignments.DeleteAllAssignment(course_id)
        return HttpResponse(status=200)   
    except Exception, e:
        errorpkg = {}        
        errorpkg['msg'] = "Error in delete all assignment."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")

#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/create/
@csrf_exempt
def k_create(request):    
    try:                         
        token = request.META['HTTP_X_AUTHORIZATION']  
        urlorigin = "https://" + request.META.get("HTTP_HOST")          
        t_mapper = getTemplateMappings(urlorigin)    
        k_payload = validateToken(token,t_mapper['JWKS_URL'])
        if k_payload.get('payload_decoded_and_verified'):        
            userid = k_payload['payload_decoded_and_verified']['sub']                   
            jsonData = json.loads(request.body)                
            retObj = RevelAssignments.CreateAssignment(jsonData,userid)
            return HttpResponse(json.dumps(retObj),
                        status=200, content_type="application/json") 
        else:
            return HttpResponse(status=403)
    except Exception, e:        
        errorpkg = {}        
        errorpkg['msg'] = "Error in create assignment." 
        errorpkg['errorobj'] = str(e)    
        errorpkg['reqbody'] = request.body   
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")

#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/update/
@csrf_exempt
def k_update(request):    
    try: 
        token = request.META['HTTP_X_AUTHORIZATION']  
        urlorigin = "https://" + request.META.get("HTTP_HOST")          
        t_mapper = getTemplateMappings(urlorigin)    
        k_payload = validateToken(token,t_mapper['JWKS_URL'])
        if k_payload.get('payload_decoded_and_verified'):  
            userid = k_payload['payload_decoded_and_verified']['sub']          
            jsonData = json.loads(request.body)                
            RevelAssignments.UpdateAssignment(jsonData,userid)  
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=403)           
    except Exception, e:        
        errorpkg = {}        
        errorpkg['msg'] = "Error in update assignment."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")

#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/copy/
@csrf_exempt
def k_copy(request):    
    try: 
        token = request.META['HTTP_X_AUTHORIZATION']  
        urlorigin = "https://" + request.META.get("HTTP_HOST")          
        t_mapper = getTemplateMappings(urlorigin)    
        k_payload = validateToken(token,t_mapper['JWKS_URL'])
        if k_payload.get('payload_decoded_and_verified'): 
            userid = k_payload['payload_decoded_and_verified']['sub']
            jsonData = json.loads(request.body)                
            retObj = RevelAssignments.CopyAssignment(jsonData,userid)  
            return HttpResponse(json.dumps(retObj),
                        status=200, content_type="application/json")   
        else:
            return HttpResponse(status=403)        
    except Exception, e:        
        errorpkg = {}        
        errorpkg['msg'] = "Error in copy assignment."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")

#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/post_grade/
@csrf_exempt
def k_post_grade(request):    
    try:   
        token = request.META['HTTP_X_AUTHORIZATION'] 
        refUrl = request.META['HTTP_REFURL'] 
        urlorigin = "https://" + request.META.get("HTTP_HOST")          
        t_mapper = getTemplateMappings(urlorigin)    
        k_payload = validateToken(token,t_mapper['JWKS_URL'])
        if k_payload.get('payload_decoded_and_verified'):            
            jsonData = json.loads(request.body)                
            datas = { 
                "provider": jsonData["provider"], 
                "rawItemScore": jsonData["rawItemScore"], 
                "submissionTime": jsonData["submissionTime"], 
                "assessmentId":  jsonData["assessmentId"],
                "assignmentId":  jsonData["assessmentId"],  
                "activityId":  jsonData["activityId"], 
                "courseId":  jsonData["courseId"], 
                "activityRevision":  jsonData["activityRevision"], 
                "actor":  jsonData["actor"]
            }
            #assessmentId - here is assignment Id.
            
            co_relation_id = request.META['HTTP_CORRELATION_ID']
            
            headers = {'X-Authorization': token, 'Content-type': 'application/json', "X-ApiKey": RevelSettings.API_KEY, "Correlation-Id":co_relation_id}
            if not refUrl.endswith("/"):
                refUrl = refUrl + "/"
            
            pdatas = {
                "provider": jsonData["provider"],
                "assessmentId":  jsonData["assessmentId"], 
                "assignmentId":  jsonData["assessmentId"], 
                "activityId":  jsonData["activityId"], 
                "courseId":  jsonData["courseId"], 
                "authToken": token                 
            }			

            postgradeurl = refUrl + "las-paf/sd/scoring/events/KnowdlSim/v4"    
            rsp1 = requests.post(postgradeurl, data=json.dumps(pdatas), headers=headers)
            
            postgradeurl = refUrl + "las-paf/sd/scoring/result/v4"    
            rsp = requests.post(postgradeurl, data=json.dumps(datas), headers=headers)
            

            #return rsp.text
            return HttpResponse(json.dumps(rsp.text + rsp1.text),
                        status=200, content_type="application/json") 
        else:
            return HttpResponse(status=403)        
    except Exception, e:        
        errorpkg = {}        
        errorpkg['msg'] = "--v--Error in grade submission."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")
        
#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/get_user/[course_id]/
@csrf_exempt
def k_get_user(request,course_id):    
    if request.method == 'POST':
        return HttpResponse(status=400)
    try:   
        token = request.META['HTTP_X_AUTHORIZATION'] 
        co_relation_id = request.META['HTTP_CORRELATION_ID'] 
        refUrl = request.META['HTTP_REFURL'] 
        urlorigin = "https://" + request.META.get("HTTP_HOST")          
        t_mapper = getTemplateMappings(urlorigin)    
        k_payload = validateToken(token,t_mapper['JWKS_URL'])
        if k_payload.get('payload_decoded_and_verified'):  
            if not refUrl.endswith("/"):
                refUrl = refUrl + "/" 
                                       
            getusrurl = refUrl + "las-api/api/courses/" + course_id + "/users/me/"            
            headers = {'X-Authorization': token, 'Content-type': 'application/json', "X-ApiKey": RevelSettings.API_KEY, "Correlation-Id":co_relation_id}
            rsp = requests.get(getusrurl,headers=headers)
            #return rsp.text
            return HttpResponse(json.dumps(rsp.json()),
                        status=200, content_type="application/json") 
        else:
            return HttpResponse(status=403)        
    except Exception, e:        
        errorpkg = {}        
        errorpkg['msg'] = "222Error in get user details 222."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")  
        

#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/get_all_user/[course_id]/
@csrf_exempt
def k_get_all_users(request,course_id):    
    if request.method == 'POST':
        return HttpResponse(status=400)
    try:   
        token = request.META['HTTP_X_AUTHORIZATION'] 
        co_relation_id = request.META['HTTP_CORRELATION_ID'] 
        refUrl = request.META['HTTP_REFURL'] 
        urlorigin = "https://" + request.META.get("HTTP_HOST")          
        t_mapper = getTemplateMappings(urlorigin)    
        k_payload = validateToken(token,t_mapper['JWKS_URL'])
        if k_payload.get('payload_decoded_and_verified'):  
            if not refUrl.endswith("/"):
                refUrl = refUrl + "/" 
                                       
            getusrurl = refUrl + "las-api/api/courses/" + course_id + "/users/"            
            headers = {'X-Authorization': token, 'Content-type': 'application/json', "X-ApiKey": RevelSettings.API_KEY, "Correlation-Id":co_relation_id}
            rsp = requests.get(getusrurl,headers=headers)
            #return rsp.text
            return HttpResponse(json.dumps(rsp.json()),
                        status=200, content_type="application/json") 
        else:
            return HttpResponse(status=403)        
    except Exception, e:        
        errorpkg = {}        
        errorpkg['msg'] = "222Error in get user details 222."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json") 
 

#https://dev.econdip.pearsoncmg.com/econservice/knowdlsim/revelintegration/assignments/validatetoken/ffffffff530ca01ae4b053c26fad1d9d/puFp5drUw2yS4UxdtawIhDKuRcRr/
@csrf_exempt
def k_validate_token(request, identity_id):    
    try:        
        r_data = json.loads(request.body)
        v_token = r_data['v_token']        
        
        urlorigin = "https://" + request.META.get("HTTP_HOST")          
        t_mapper = getTemplateMappings(urlorigin)    
        
        
        vmsg = jwtValidator.validateToken(v_token, t_mapper['JWKS_URL'])        
            
        return HttpResponse(json.dumps(vmsg),
                        status=200, content_type="application/json")         
        
    except Exception, e:        
        errorpkg = {}        
        errorpkg['exception'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")        
        

#Anu 11-nov-2017 save/get revel assignment settings
@csrf_exempt
def k_saveAssignmentSettings(request, course_id, assignment_id,template_id):    
    try:
        msg = "Assignment settings added successfully."        
        jsondata = request.POST.get('settings_object', "{}")                
        if assignment_id is not None and course_id is not None :
            RevelAssignmentDetails.saveSettings(course_id, assignment_id, template_id, jsondata)
        else :
            msg = "Assignment id or course id is missing"
        
        return HttpResponse(json.dumps(msg),
                        status=200, content_type="application/json")
    except Exception, e:  
        errorpkg = {}      
        errorpkg['msg'] = "Error in SaveAssignmentSettings."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")

@csrf_exempt
def k_getAssignmentSettings(request, course_id, assignment_id, template_id):
    asgn_settings = {}
    try:
        a_setiings = RevelAssignmentDetails.getSettings(course_id, assignment_id, template_id) 
        if a_setiings is not None:             
            asgn_settings['settingsData'] = json.loads(a_setiings.settingsData) 
            if a_setiings.objectiveDetails != None and a_setiings.objectiveDetails != "":
                try:
                    asgn_settings['objectiveDetails'] = json.loads(a_setiings.objectiveDetails)
                except Exception as ex:
                    asgn_settings['objectiveDetails'] = {}
                    
                    
        return HttpResponse(json.dumps(asgn_settings),
                        status=200, content_type="application/json")        
    except Exception, e:  
        errorpkg = {}      
        errorpkg['msg'] = "Error in GetAssignmentSettings."
        errorpkg['errorobj'] = str(e)        
        return HttpResponse(json.dumps(errorpkg),
                        status=500, content_type="application/json")
        

@csrf_exempt
def k_process(request, course_id, assignment_id, template_id, command):    
    tracestr = "start process444"    
    jsondatavalues = ""
    returnResponse = ""
    try :
        tracestr = tracestr + " command:"  + command + ",course_id:" +  course_id + ",assignment_id" + assignment_id + ",template_id:" + template_id
        jsondatavalues = json.loads(request.POST.get('jsondata', None))                       
        if command == "launch" :
            retjson = attemptlaunch(course_id, assignment_id, template_id, jsondatavalues)            
            return HttpResponse(json.dumps(retjson),
                        status=200, content_type="application/json")  
                       
        elif command == "updateattemptdata" :
            returnResponse = updateAttemptData(course_id, assignment_id, template_id,jsondatavalues)            
        elif command == "classaverage" :
            returnResponse = getClassAverage(course_id, assignment_id, template_id)
            return HttpResponse(returnResponse)        
            
    except Exception as e :            
            returnResponse = str(e)
                                        
    return HttpResponse(tracestr + returnResponse)





@csrf_exempt
def getAttemptCount(request, course_id, assignment_id, template_id, student_id):
    attemptscnt=0
    try:
        attemptscnt = RevelMasterAttemptData.objects.filter(assignmentId=assignment_id, courseId=course_id, templateId=template_id, Student_Id = student_id, CompletionStatus = 'complete' ).count()
    except Exception as ex:
        attemptscnt = 0
    return HttpResponse(attemptscnt)

@csrf_exempt
def getAttemptData(request, course_id, assignment_id, template_id, student_id):
    retJson = {}
    try :
        attNo = int(request.GET.get("attno", -1))
        asgnDetails = RevelAssignmentDetails.get(course_id, assignment_id, template_id)        
        if asgnDetails.settingsData != None and asgnDetails.settingsData != "" :            
            retJson["settings"] = asgnDetails.settingsData            
        else:
            retJson["settings"] = "{AllowedAttempts:0, ShowClassAvg:true, TargetPoints:1}"
            
        atmpt = RevelMasterAttemptData.objects.filter(courseId=course_id, assignmentId=assignment_id, templateId=template_id, Student_Id = student_id).order_by("StartDate").all()[attNo-1]
        retJson["StateData"] = json.loads(atmpt.stateData)
        retJson["RequestNo"] = atmpt.additionalField1
        retJson["TotalTimeSpent"] = str(atmpt.TimeSpent)
        
        attemptscnt=0
	bestScore = "0"
	try:
            compattmts = RevelMasterAttemptData.objects.filter(courseId=course_id, assignmentId=assignment_id, templateId=template_id, Student_Id = student_id, CompletionStatus = 'complete' ).all() 
	    attemptscnt = compattmts.count()             
            bestScore = str( compattmts.aggregate(Max('Score'))['Score__max'])
	except Exception as ex:
            attemptscnt = 0
	    bestScore = "0" 
    
        retJson["CompletedAttemptCount"] = attemptscnt
	retJson["bestScore"] = bestScore
                        
    except Exception as excp :
        retJson["Error"] = str(excp)
	retJson["StateData"] = "{}"
        
    return HttpResponse(json.dumps(retJson), status=200, content_type="application/json")       
    

def getClassAverage(cId, aId, tId) :
    returnValue =""
    try :
        filterAvg = {"courseId": cId,"assignmentId": aId, "templateId" :tId}
        asgnDetails = RevelAssignmentDetails.objects.get(**filterAvg)            
        if  asgnDetails.numOfUsers > 0 :
            returnValue = asgnDetails.totalScore/Decimal(str(asgnDetails.numOfUsers))            
    except Exception as excp :
        returnValue = str(0.0)
            
    return returnValue

def attemptlaunch(cId, aId, tId, jsondatavalues) :
    returnValue = "Start Launch444"
    objDetails = ""
    createAtt = "no"
    sId = "" 
    allowedAttempts = 0 
    allowSubmission = "true" 
    retJson = {}       
    try : 
        returnValue = returnValue + "get assignment details"
        asgnDetails = RevelAssignmentDetails.get(cId, aId, tId)   
        returnValue = returnValue + "end get assignment details"                     
        if "ObjectiveDetails" in jsondatavalues :
            objDetails = jsondatavalues["ObjectiveDetails"] 
            
        if "CreateAttempt" in jsondatavalues :
            createAtt = jsondatavalues["CreateAttempt"] 
            
        returnValue = returnValue + "objDetails:" + str(objDetails)  
            
        if objDetails is not None and objDetails!="" and objDetails!="{}":  
            returnValue = returnValue + "Save objdetails"
            asgnDetails.objectiveDetails = str(objDetails)
            asgnDetails.lastUpdateDate = datetime.datetime.now()
            asgnDetails.lastUpdateFor = "Updated Objective Details."
            asgnDetails.save()
            returnValue = returnValue + "done Save objdetails"
            
        settingsDataJson = {}  
        returnValue = returnValue + "load settings"
        if asgnDetails.settingsData != None and asgnDetails.settingsData != "" :            
            settingsDataJson = json.loads(asgnDetails.settingsData)
            retJson["settings"] = asgnDetails.settingsData
            if "AllowSubmission" in settingsDataJson:
                allowSubmission = str(settingsDataJson["AllowSubmission"])
                
            if "AllowedAttempts" in settingsDataJson:
                allowedAttempts = settingsDataJson["AllowedAttempts"]
        else:
            retJson["settings"] = "{AllowedAttempts:0, ShowClassAvg:true, TargetPoints:1}"
            
        returnValue = returnValue + "load settings"
        retJson["dueDateMode"] = "do"
        if allowSubmission == "false":            
            cnt = RevelAssignments.objects.filter(courseId=cId, assignmentId= aId, templateId= tId, dueTime__gt = datetime.datetime.now()).count()
            if cnt == 0:
                retJson["dueDateMode"] = "preview"
               
        if "Student_Id" in jsondatavalues :
            sId= jsondatavalues["Student_Id"]
             
        returnValue = returnValue + "studentId:" + sId          
        if sId != "":                   
            filter1 = {"courseId": cId,"assignmentId": aId, "templateId" :tId, "Student_Id" :sId} 
            returnValue = returnValue + "get attempt count"                  
            attCount = RevelMasterAttemptData.objects.filter(**filter1).count()
            returnValue = returnValue + "attCount:" + str(attCount)
            if attCount <=0:
                if allowedAttempts == None or allowedAttempts <= 0 or (allowedAttempts > 0 and attCount < allowedAttempts) :                
                    returnValue = returnValue + " Creating new Attempt(will get inprogress attempt)" 
                    atmpt = RevelMasterAttemptData.create(cId, aId, tId, sId, jsondatavalues) 
                    retJson["StateData"] = json.loads(atmpt.stateData)#.encode('ascii', 'replace') 
                    retJson["RequestNo"] = atmpt.additionalField1
                    retJson["TotalTimeSpent"] = str(atmpt.TimeSpent)
                    retJson["CompletedAttemptCount"] = 0
		    retJson["bestScore"] = "0"
                    returnValue = returnValue + " Created new Attempt. AttemptId:" + str(atmpt.Id)
                    returnValue = returnValue + "Update User Count"                  
                    asgnDetails.numOfUsers = asgnDetails.numOfUsers + 1                    
                    asgnDetails.save()
                    returnValue = returnValue + "Total Users:" + str(asgnDetails.numOfUsers) 
            else:
                returnValue = returnValue + "createAtt:" + createAtt 
                if createAtt == "yes":
                    returnValue = returnValue + "allowedAttempts:" + str(allowedAttempts) + "attCount:" + str(attCount)
                    if allowedAttempts == None or allowedAttempts <= 0 or (allowedAttempts > 0 and attCount < allowedAttempts) :
                        returnValue = returnValue + "flagbased create"
                        atmpt = RevelMasterAttemptData.create(cId, aId, tId, sId, jsondatavalues) 
                        retJson["StateData"] = json.loads(atmpt.stateData)
                        retJson["RequestNo"] = atmpt.additionalField1
                        retJson["TotalTimeSpent"] = str(atmpt.TimeSpent)
                else:
                    returnValue = returnValue + "get last attempt"
                    atmpt = RevelMasterAttemptData.getLast(cId, aId, tId, sId) 
                    retJson["StateData"] = json.loads(atmpt.stateData) 
                    retJson["RequestNo"] = atmpt.additionalField1
                    retJson["TotalTimeSpent"] = str(atmpt.TimeSpent)
                    
                attemptscnt = 0
		bestScore = "0"
                try:
                    compattmts = RevelMasterAttemptData.objects.filter(assignmentId=aId, courseId=cId, templateId=tId, Student_Id = sId, CompletionStatus = 'complete' ).all()
		    attemptscnt = compattmts.count()
                    bestScore = str( compattmts.aggregate(Max('Score'))['Score__max'])
                except Exception as ex:
                    attemptscnt = 0
		    bestScore = "0"
                
                retJson["CompletedAttemptCount"] = attemptscnt
		retJson["bestScore"] = bestScore            
                            
    except Exception as e :            
        returnValue =  returnValue + "Error-" +  str(e)  
        
    retJson["TraceData"] = returnValue  
    
    return retJson

def updateAttemptData(cId, aId, tId, jsondatavalues) :
    returnValue = "Start updateAttemptData444"
    sId = ""
    completionStatus = ""
    stateData = ""
    overallScore = 0.0
    overallTimeSpent= 0.0
    overallPoints = 0.0
    RequestNo = 0
    
    try : 
        if "Student_Id" in jsondatavalues :
            sId= jsondatavalues["Student_Id"]
            
        if "CompletionStatus" in jsondatavalues :
            completionStatus = jsondatavalues["CompletionStatus"] 
            
        if "OverallScore" in jsondatavalues :
            overallScore = Decimal(str(jsondatavalues["OverallScore"])) 
        
        if "OverallTimeSpent" in jsondatavalues :
            overallTimeSpent = Decimal(str(jsondatavalues["OverallTimeSpent"])) 
        
        if "OverallPoints" in jsondatavalues :
            overallPoints = Decimal(str(jsondatavalues["OverallPoints"])) 
        
        if "RequestNo" in jsondatavalues :
	    if jsondatavalues["RequestNo"] != "":
                RequestNo = int(str(jsondatavalues["RequestNo"]))
            
        if "StateData" in jsondatavalues :
            stateData = json.dumps(jsondatavalues["StateData"])      
        
        filter1 = {"courseId": cId,"assignmentId": aId, "templateId" :tId, "Student_Id" :sId, "CompletionStatus":"inprogress"}
        returnValue = returnValue + "filter1:" + str(filter1)   
                
        inprgAtt = None
        try:
            inprgAtt =   RevelMasterAttemptData.objects.get(**filter1)
        except Exception as e :  
            returnValue = returnValue + "Error In fetch master attempt"              
            inprgAtt = None
            
        returnValue = returnValue + "--Attempt Update"   
        
        if inprgAtt is not None : 
            returnValue = returnValue + "--Attempt Update" 
            dbreqno =0
            try:
                if inprgAtt.additionalField1 != "":
                    dbreqno = int(inprgAtt.additionalField1)
            except Exception as mexxx:
                dbreqno = 0
                
            returnValue = returnValue + "--dbreqno:" + str(dbreqno) + "--RequestNo:" + str(RequestNo)     
            if dbreqno == 0 or RequestNo == 0 or (dbreqno <= RequestNo):                                       
                maxscore = 0.0        
                filterMaxScr = {"courseId": cId,"assignmentId": aId, "templateId" :tId, "Student_Id" :sId, "ReportStatus" : "active", "CompletionStatus":"complete"}        
                try:
                    returnValue = returnValue + "--get maxscore"
                    maxscore =   RevelMasterAttemptData.objects.filter(**filterMaxScr).values_list("Score",flat=True)[0] 
                except Exception as e :                          
                    maxscore = 0.0  
                    
                returnValue = returnValue + "--maxscore:" + str(maxscore)
                    
                if overallScore is None:
                    overallScore = 0.0            
                inprgAtt.Score = overallScore
                inprgAtt.Points = overallPoints
                inprgAtt.stateData = stateData
                inprgAtt.additionalField1 = str(RequestNo)
                
                if overallTimeSpent != 0 :
                    inprgAtt.TimeSpent = overallTimeSpent                
                
                returnValue = returnValue + "--completionStatus:" + str(completionStatus)
                    
                if completionStatus != "" and completionStatus.lower() == "complete" : 
                    inprgAtt.CompletionStatus = completionStatus.lower()
                    returnValue = returnValue + "--score:" + str(inprgAtt.Score)
                    if inprgAtt.Score is not None and maxscore < inprgAtt.Score:
                        inprgAtt.ReportStatus = "active"
                        scorediff = Decimal(str(inprgAtt.Score)) - Decimal(str(maxscore))
                        returnValue = returnValue + "--scorediff:" + str(scorediff)
                        asgnDetailsfilter = {"courseId": cId,"assignmentId": aId, "templateId" :tId}
                        asgnDetails = RevelAssignmentDetails.objects.get(**asgnDetailsfilter)
                        asgnDetails.totalScore = asgnDetails.totalScore + scorediff                    
                        asgnDetails.save()
                        returnValue = returnValue + "--totalScore:" + str(asgnDetails.totalScore)
                        
                    inprgAtt.EndDate = datetime.datetime.now()
                    
                    #Update other attempts  
                    returnValue = returnValue + "--ReportStatus:" + str(inprgAtt.ReportStatus)                  
                    if inprgAtt.ReportStatus == "active" :
                        filterRStat = {"courseId": cId,"assignmentId": aId, "templateId" :tId, "Student_Id" :sId} 
                        RevelMasterAttemptData.objects.filter(**filterRStat).exclude(Id = inprgAtt.Id).update(ReportStatus = "inactive")
                        returnValue = returnValue + "--ReportStatus Update complete:"
                
                inprgAtt.save()
                        
            addquesdetail = AddQuestionDetails(inprgAtt, jsondatavalues)                   
            returnValue = returnValue + addquesdetail
        
        returnValue = returnValue + " - Update Attempt Data Success"
    except Exception as e :            
            returnValue = returnValue + str(e) 
            
    return returnValue

def AddQuestionDetails(mstAttempt, jsondatavalues):
    retval = 'Start AddQuestionDetails:'
    qId ,pId ,qText ,qOptions ,qSelOptionId ,qCorrectStatus ,qTitle ,qtype = "","","","","","","",""
    qAdditionalInfo ,q_mqAdditionalInfo  ={} ,{}
    qTimespent = 0.0
    qScore = 0.0
    qPoints = 0.0
    qTotal = 0.0    
    QDetails = {}
    
    if "QDetails" in jsondatavalues :
        QDetails = jsondatavalues["QDetails"]    
    else :
        return retval + "-Not a Question"
    
    if "QId" in QDetails :
        qId = QDetails["QId"]
                
    if "PId" in QDetails :
        pId = QDetails["PId"]
    
    if "QText" in QDetails :
        qText = QDetails["QText"]
                
    if "QOptions" in QDetails :
        qOptions = QDetails["QOptions"]
    
    if "QSelOptionId" in QDetails :
        qSelOptionId = QDetails["QSelOptionId"]
    
    if "QCorrectStatus" in QDetails :
        qCorrectStatus = QDetails["QCorrectStatus"]
        
    if "QTimeSpent" in QDetails :
        qTimespent = Decimal(str(QDetails["QTimeSpent"]))
            
    if "QScore" in QDetails :
        qScore = Decimal(str(QDetails["QScore"]))
    
    if "QPoints" in QDetails :
        qPoints = Decimal(str(QDetails["QPoints"]))
    
    if "QTotal" in QDetails :
        qTotal = Decimal(str(QDetails["QTotal"]))
    
    if "AdditionalInfo" in QDetails :
        qAdditionalInfo = QDetails["AdditionalInfo"]
    
    if "MQAdditionalInfo" in QDetails :
        q_mqAdditionalInfo = QDetails["MQAdditionalInfo"]
        
    if "QTitle" in QDetails :
        qTitle= QDetails["QTitle"]
    
    if "Type" in QDetails :
        qtype = QDetails["Type"]
        
    if qId is not None and qId != "" and mstAttempt is not  None :
        try:
            filtermstQues = {"courseId" : mstAttempt.courseId ,"templateId" : mstAttempt.templateId,"PageId" : pId, "QuestionId":qId}            
            masterQuest = None
            try:
                masterQuest = RevelMasterQuestions.objects.get(**filtermstQues)  
            except Exception as e:
                masterQuest = None
                                      
            if masterQuest is None:  
                retval = retval + "-- create master question entry"                            
                masterQuest = RevelMasterQuestions.objects.create(courseId = mstAttempt.courseId, templateId = mstAttempt.templateId,
                    PageId = pId, QuestionId = qId, QuestionText = qText, TotalPoints = qTotal,Options = qOptions,
                    QuestionTitle = qTitle, Type = qtype, AdditionalInfo = str(q_mqAdditionalInfo))
                retval = retval + "-- create master question entry success:"
            
            filterQAtmpt = {"MstAttemptId" : mstAttempt.Id, "PageId" : pId , "QuestionId": qId}
            
            quesAttemptDetail = None
            try:
                quesAttemptDetail = RevelQuestionAttemptDetails.objects.get(**filterQAtmpt)
            except Exception as e:
                quesAttemptDetail = None                
            
            if quesAttemptDetail is None: 
                retval = retval + "-- create question attempt entry"
                qlqad = RevelQuestionAttemptDetails.objects.create(MstAttemptId = mstAttempt.Id, PageId = pId, QuestionId = qId, 
                                                                   CorrectStatus = qCorrectStatus, TimeSpent = qTimespent, Score = qScore,
                                                                   Points = qPoints, SelOptionId = qSelOptionId, AdditionalInfo = str(qAdditionalInfo))
                retval = retval + "-- create question attempt entry success"
            
        except Exception as ine:
            retval = retval + "---AddQuestionDetails Error:" + str(ine)
            
    return retval

#https://dev.econdip.pearsoncmg.com/econservice/data/econ/common_services/get_asgn_data/ 
@csrf_exempt
def k_getAssignmentData(request):
    tracestr = "Start GetAssignmentData 1000:"
    yval = int(request.GET.get('y', "2017"))
    mval = int(request.GET.get('m', "11"))
    dval = int(request.GET.get('d', "14"))    
    paramasgnId = request.GET.get('aId', "")   
    paramisdelete = request.GET.get('isdelete', "no")   
    paramgetstdata= request.GET.get('getSD', "no")    
    courseIdList = []
    assignidList = []
        
    assignList = []
    try:
        tracestr = tracestr + "paramisdelete:" + paramisdelete + "--paramasgnId" + paramasgnId
        
        if paramisdelete == "yes":
            mstAttIds = RevelMasterAttemptData.objects.filter(assignmentId = paramasgnId).values_list("Id",flat=True)
            delvallist = RevelAssignmentDetails.objects.filter(assignmentId = paramasgnId).values("templateId","courseId").all()
            if delvallist.count()>0:
                navcrseId = delvallist[0]["courseId"]
                navtempId = delvallist[0]["templateId"]
                RevelMasterQuestions.objects.filter(templateId = navtempId, courseId = navcrseId).delete()
                
            RevelQuestionAttemptDetails.objects.filter(MstAttemptId__in = mstAttIds).delete()
            RevelMasterAttemptData.objects.filter(assignmentId = paramasgnId).delete()
            
            
        begin_date = datetime.date(yval, mval, dval)     
        tracestr = tracestr + "BeginDate:" + datetime.datetime.combine(begin_date, datetime.time.max).strftime("%Y-%m-%d %H:%M:%S")
        valueslist = RevelMasterAttemptData.objects.filter(StartDate__gt = datetime.datetime.combine(begin_date, datetime.time.max)).values("courseId", "assignmentId").all()
        if paramasgnId !="":
            valueslist = RevelMasterAttemptData.objects.filter(assignmentId = paramasgnId, StartDate__gt = datetime.datetime.combine(begin_date, datetime.time.max)).values("courseId", "assignmentId").all()
        
        tracestr = tracestr + "valueslist.count()" + str(valueslist.count())
        if valueslist.count()>0:
            for lval in valueslist:
                assignidList.append(lval["assignmentId"])
                courseIdList.append(lval["courseId"])        
        
        tracestr = tracestr + "Fetching Assignment List-->"
        assignments = RevelAssignmentDetails.objects.filter(assignmentId__in = assignidList , courseId__in = courseIdList).all()
        for asgn in assignments:
            asgnobj = {}  
            try:                              
                asgnobj["assignmentId"] = asgn.assignmentId
                asgnobj["courseId"] = asgn.courseId
                asgnobj["templateId"] = asgn.templateId
                asgnobj["totalScore"]  = str(asgn.totalScore)
                asgnobj["numOfUsers"] = str(asgn.numOfUsers)
                asgnobj["settingsData"] = asgn.settingsData                
                
            
                tracestr = tracestr + "Completed Fetching Assignment List-->"    
                tracestr = tracestr + "Fetching Attempts List-->"
                attempts = RevelMasterAttemptData.objects.filter(assignmentId = asgn.assignmentId ,StartDate__gt = datetime.datetime.combine(begin_date, datetime.time.max)).all()
                tracestr = tracestr + "Completed Fetching Attempt List-->" 
                       
                AttemptArray = []
                for att in attempts:
                    attobj = {}        
                    try:        
                        attobj["Id"] = att.Id
                        attobj["courseId"] = att.courseId
                        attobj["assignmentId"] = att.assignmentId                
                        attobj["templateId"] = att.templateId
                        attobj["Student_Id"] = att.Student_Id
                        attobj["StudentName"] =att.StudentName
                        attobj["Role"] =att.Role
                        attobj["StartDate"] = att.StartDate.strftime("%Y-%m-%d %H:%M:%S")
                        attobj["EndDate"] = att.EndDate.strftime("%Y-%m-%d %H:%M:%S")                
                        attobj["TimeSpent"] = str(att.TimeSpent)
                        attobj["Score"] = str(att.Score)
                        attobj["Points"] = str(att.Points)                
                        attobj["ReportStatus"] = att.ReportStatus
                        attobj["CompletionStatus"] = att.CompletionStatus  
                        if paramgetstdata == "yes" :
                            attobj["StateData"] = att.stateData
                                   
                        try:
                            detArr = []
                            attdetails = RevelQuestionAttemptDetails.objects.filter(MstAttemptId = att.Id).all()  
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
                asgnobj["Attempts"] = AttemptArray 
                
            except Exception as innerex2:
                tracestr = tracestr + "Error In Parsing Assignment Data: Assignment_Id" + asgn.assignmentId + "-Exception:" + str(innerex2)                        
                   
            assignList.append(asgnobj) 
               
        tracestr = tracestr + "Trace Complete."
        
    except Exception as mainEx:
        tracestr = tracestr + "Main Exception1:" + str(mainEx)
    
    retJson = {}
    retJson["TraceData"] = tracestr
    retJson["AssignmentData"] = assignList    
    
    return HttpResponse(json.dumps(retJson),
                        status=200, content_type="application/json")           

@csrf_exempt
def showpage(request):
    pagedata = request.POST.get('pagehtml', "<h1>No data received</h1>")
    return HttpResponse(json.dumps(retJson), status=200, content_type="text/html")

# Analytics views.py file .
#from knowdlanalytics import models as m
from knowdlsim import Classes
#from econ_service_project.knowdlsim import models as revelM
from knowdlsim import models as revelM
#revelM = __import__("econ_service_project.knowdlsim") 
#Vinod pls uncomment below line and comment above line while integration
#revelM = __import__("econ-service-project.knowdlsim")
from django.shortcuts import render_to_response
from django.template import RequestContext
from __builtin__ import str, int
from ast import literal_eval
from django.db.models import Avg
from django.views.decorators.csrf import csrf_exempt
import requests

k_ANALYTICS_STATIC = 'content/staticfiles/revelanalytics/'

#Anu 25-oct-2017 for QLInteractionController
def DummyPage(request):
    returnResponse = "we can call method this way"    
    context = RequestContext(request)  
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Message' : returnResponse } 
    return render_to_response('NewFile.html', context_dict, context_instance = context)


def DBLog(msg, ex) :
    logstr = msg 
    if ex is not None :
        logstr = logstr + "==== ExceptionMessage:" + str(ex)+ ", ExceptionStacktrace:" 
               
    #m.tbl_LogEntries.objects.create(LogDate = datetime.now(),LogString = logstr)

@csrf_exempt        
def RevelTrendsAcrossQues(request):
    
    qlLst = [] 
    
    #locLst = GetLocationList()          
    
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'ql_list': qlLst }
 
    return render_to_response('RevelTrendsAcrossQues.html', context_dict, context_instance = context)

@csrf_exempt
def RevelTrendsAcrossQuesDetails(request):
    selsim = request.GET.get('selsim', None)
    selloc = request.GET.get('selloc', None)
    
    qlQDRV = GetQuestionDetailsModel(selsim, selloc)
    
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('RevelTrendsAcrossQuesDetails.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'QLReportView': qlQDRV }
 
    return render_to_response('RevelTrendsAcrossQuesDetails.html', context_dict, context_instance = context)


#https://dev.econdip.pearsoncmg.com/econservice/knowdlanalytics/RevelAnalytics/
@csrf_exempt
def RevelAnalytics(request):
    #Anu 14-nov-2017 module and structure renamed changes
    Template_Id = request.GET.get('QL_Id', '')
    ASGN = request.GET.get('ASGN', '')
    Course_Id = request.GET.get('Course_Id', '')
    
    qlLst = None
    asgnLst = None
           
    if Template_Id == "" and ASGN == "" :
        qlLst = []#GetSimList()
        asgnLst = []#GetAssignmentList()
    
    # Obtain the context from the HTTP request.
    
    context = RequestContext(request)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'ql_list': qlLst, 'asgn_list' : asgnLst }
  
    return render_to_response('RevelAnalytics.html', context_dict, context_instance = context)

@csrf_exempt
def RevelAnalyticsDetails(request):
    #Anu 14-nov-2017 module and structure renamed changes
    templateId = request.GET.get('QL_Id', None)
    #LOC = request.GET.get('LOC', None)
    ASGN = request.GET.get('ASGN', None)
    courseId = request.GET.get('Course_Id', '')
        
    if templateId!="" and ASGN != "" and courseId !="" :
        filter1 = {"assignmentId": ASGN,"templateId": templateId, "courseId" : courseId}
        AssignmentTitle = revelM.RevelAssignments.objects.filter(**filter1).values("title").distinct()            
    else :
        AssignmentTitle = ""
    
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'AssignmentTitle': AssignmentTitle }
  
    return render_to_response('RevelAnalyticsDetails.html', context_dict, context_instance = context)


@csrf_exempt
def RevelOverview(request):
    #Anu 14-nov-2017 module and structure renamed changes
    
    templateId = request.GET.get('QL_Id', None) # selsim
    #selloc = request.GET.get('LOC', None)
    ASGN = request.GET.get('ASGN', None)
    courseId = request.GET.get('Course_Id', '')
    
    qlQDRV = GetQuestionDetailsModel(templateId, courseId , ASGN)
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('RevelOverview.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'QLReportView': qlQDRV }
 
    return render_to_response('RevelOverview.html', context_dict, context_instance = context)


@csrf_exempt
def RevelClassReport(request):
    #Anu 14-nov-2017 module and structure renamed changes
    
    templateId = request.GET.get('QL_Id', None)
    courseId = request.GET.get('Course_Id', '')
    ASGN = request.GET.get('ASGN', None)
    
    qlQDRV = GetQuestionDetailsModel(templateId, courseId, ASGN, True)
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('RevelClassReport.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'QLReportView': qlQDRV }
 
    return render_to_response('RevelClassReport.html', context_dict, context_instance = context)


@csrf_exempt
def RevelStudentReport(request):
    #Anu 14-nov-2017 module and structure renamed changes
    templateId = request.GET.get('QL_Id', None)
    #selloc = request.GET.get('LOC', None)
    ASGN = request.GET.get('ASGN', None)
    courseId = request.GET.get('Course_Id', '')
    
    qlQDRV = GetStudentDetailModel(templateId, courseId, ASGN,"")
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('RevelStudentReport.html', { "Status" : "No data found" }, context_instance = context)
    
    urlOrigin = "https://" + request.META.get("HTTP_HOST")
    r = requests.get(urlOrigin + '/knowdl_revel_sim/commonfiles/template_mappings.json')
    if r.status_code == 200:
        template_mappings = r.json()
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'QLReportView': qlQDRV, 'TemplateURL': urlOrigin + template_mappings[templateId] }
 
    return render_to_response('RevelStudentReport.html', context_dict, context_instance = context)

#deva 24-nov-2017 - to show the student attempt details by id
@csrf_exempt
def RevelIndivisualStudentReport(request):
    
    templateId = request.GET.get('QL_Id', None)
    ASGN = request.GET.get('ASGN', None)
    courseId = request.GET.get('Course_Id', '')
    studId = request.GET.get('STUId', None)
    
    qlQDRV = GetStudentDetailModel(templateId, courseId, ASGN, studId)
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('RevelStudentReport.html', { "Status" : "No data found" }, context_instance = context)
    
    urlOrigin = "https://" + request.META.get("HTTP_HOST")
    #new file 25/11/17 2:48pm
    r = requests.get(urlOrigin + '/knowdl_revel_sim/commonfiles/template_mappings.json')
    if r.status_code == 200:
        template_mappings = r.json()
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'QLReportView': qlQDRV, 'TemplateURL': urlOrigin + template_mappings[templateId] }
 
    return render_to_response('RevelIndividualStudentReport.html', context_dict, context_instance = context)

@csrf_exempt
def RevelOutcomes(request):  
    #Anu 14-nov-2017 module and structure renamed changes
    templateId = request.GET.get('QL_Id', None)
    #selloc = request.GET.get('LOC', None)
    ASGN = request.GET.get('ASGN', None)
    courseId = request.GET.get('Course_Id', '')
    
    qlQDRV = GetOutcomesModel(templateId, courseId, ASGN)
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('RevelOutcomes.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'QLReportView': qlQDRV }
 
    return render_to_response('RevelOutcomes.html', context_dict, context_instance = context)
   


def GetOutcomesModel(templateId, courseId, ASGN = "") :
    templateId = templateId.decode('unicode-escape')
    
    model = Classes.RevelOutcomesModel()
    filterASGN = {"templateId": templateId}
    if ASGN :
        filterASGN["assignmentId"] = ASGN 
        
    assignment = revelM.RevelAssignmentDetails.objects.filter(**filterASGN).values("objectiveDetails").all()    
    
    if assignment.count() == 0 :
        return model
    
    asgnob = assignment[0]
    jsonObjDetail = literal_eval(asgnob["objectiveDetails"])
    model.Description = str(jsonObjDetail["Title"])
    model.Title = str(jsonObjDetail["CustomTarget"])
    
    filterASGN['ReportStatus'] = 'active'
    mstattempts = revelM.RevelMasterAttemptData.objects.filter(**filterASGN).all()
    
    #get total attempted count
    mstattempids = mstattempts.values_list("Id")
    model.TotalAttempted = mstattempts.values("Student_Id").distinct().count()
    #ObjectiveDetails key here is from json object
    j_objectives = jsonObjDetail["ObjectiveDetails"]
    model.ChartData = "["
    for obj in j_objectives :
        objective = Classes.RevelOutcomeObjectiveModel()
        objective.Id = obj["Id"]
        objective.Name = obj["Name"]
        objective.Title = obj["Title"]
        objective.Questions = [] #new List<RevelOutcomesQuestionModel>()
        j_pageids = obj["PageIds"]
        pageids = []
        for pg in j_pageids :
            question = Classes.RevelOutcomesQuestionModel()
            question.QuestionId = pg
            filterQues = {"templateId": templateId,  "QuestionId" : question.QuestionId }
            masterQ = revelM.RevelMasterQuestions.objects.filter(**filterQues).all()
            if masterQ is not None and masterQ.count() > 0 :
                mQues = masterQ[0]
                question.QuestionText = mQues.QuestionText
                question.QuestionTitle = mQues.QuestionTitle
                filterScr = {"QuestionId" : question.QuestionId, "MstAttemptId__in" : mstattempids }
                attscorequery = revelM.RevelQuestionAttemptDetails.objects.filter(**filterScr)                            
                if attscorequery is not None and attscorequery.count() > 0 :                    
                    question.PresentedCount = attscorequery.values("Score").count()
                    avgscr = attscorequery.aggregate(Avg('Score'))
                    if avgscr.__len__() > 0 :
                        question.AverageScore = round(avgscr["Score__avg"] , 2)
                    else :
                        question.AverageScore = 0
                else :
                    question.PresentedCount = 0
                    question.AverageScore = 0                

                pageids.append(question.QuestionId)
                objective.Questions.append(question)
            # if ends masterQ
        # for ends pageids
        
        filterScr1 = {"QuestionId__in" : pageids, "MstAttemptId__in" : mstattempids }
        presscorelist = revelM.RevelQuestionAttemptDetails.objects.filter(**filterScr1)
        if presscorelist is not None and presscorelist.count() > 0 :
            objective.PresentedCount = presscorelist.values("Score").count()
            avgscr1 = presscorelist.aggregate(Avg('Score'))
            if avgscr1.__len__() > 0 :
                objective.AverageScore = round(avgscr1["Score__avg"] , 2)
            else :
                objective.AverageScore = 0
        else :
            objective.PresentedCount = 0
            objective.AverageScore = 0                        

        model.Objectives.append(objective)
        if model.ChartData == "[" :        
            model.ChartData = model.ChartData + "['" + objective.Name + "'," + str(objective.AverageScore) + "]"        
        else :        
            model.ChartData = model.ChartData + ",['" + objective.Name + "'," + str(objective.AverageScore) + "]"

    # for ends j_objectives    
    model.ChartData = model.ChartData + "]"
               
    return model
    
def GetStudentDetailModel(templateId, courseId, ASGN = "", STUId = "") :
    #Anu 14-nov-2017 module and structure renamed changes
    templateId = templateId.decode('unicode-escape')
    
    filter1 = {"templateId": templateId}
    	
    lstQLMasterQ = revelM.RevelMasterQuestions.objects.filter(**filter1).all()
    
    filter2 = {"templateId": templateId, 'ReportStatus' : 'active'}

    if STUId != "" : 
    	filter2 = {"templateId": templateId, 'ReportStatus' : 'active', "Student_Id" : STUId }


    qlMasterAttempts = None
    
    if ASGN :
        filter2["assignmentId"] = ASGN 
        qlMasterAttempts = revelM.RevelMasterAttemptData.objects.filter(**filter2)
    else :
        qlMasterAttempts = revelM.RevelMasterAttemptData.objects.filter(**filter2)
    
    if qlMasterAttempts.count() == 0 :
        return "No data found"
    
    lstQLMasterAttemptsId = qlMasterAttempts.values_list("Id")
    
    filter3 = {'MstAttemptId__in' :lstQLMasterAttemptsId }
    lstQLQuestionAttemptDetails = revelM.RevelQuestionAttemptDetails.objects.filter(**filter3).all()
    
    qlSRV = Classes.RevelStudentReportView()
    qlSRV.Results = []  # List<QLStudentDetails>()
    qlSRV.QuestionsDetails = [] # List<QlQuestionMasterForStudentReport>()
    
    for qlMa in qlMasterAttempts :
        student = Classes.RevelStudentDetails()
        stuattempts = None
        student.Name = qlMa.StudentName 
        student.Id = qlMa.Student_Id 
        student.MasterAttemptId = qlMa.Id
        student.Score = 0.0 if qlMa.Score is None else qlMa.Score
        student.CompletionStatus = "Completed"  if qlMa.CompletionStatus == "complete" else "In Progress"
        
        stuattempts = None
        
        filterSAttmpt = {"templateId": templateId, 'CompletionStatus' : 'complete'}
        if ASGN :
            filterSAttmpt["Student_Id"] = qlMa.Student_Id
            filterSAttmpt["assignmentId"] = ASGN            
            stuattempts = revelM.RevelMasterAttemptData.objects.filter(**filterSAttmpt).all()
        else :
            stuattempts = revelM.RevelMasterAttemptData.objects.filter(**filterSAttmpt).all()
        
        student.Attempts = []  # List<QLStudentAttempt>()
        if stuattempts is not None and stuattempts.count() > 0 :
            k = 1 
            for std in stuattempts : 
                statt = Classes.RevelStudentAttempt()
                statt.AttemptNo = k
                statt.Score =  0.00 if std.Score is None else std.Score
                #statt.SessionId = std.Session_Id
                student.Attempts.append(statt)
                k = k + 1
        # end if stuattempts is not None and stuattempts.count() > 0 :
        
        student.Questions = []  # List<RevelQuestionForStudentReport>()
        filterSQues = { "MstAttemptId" : qlMa.Id}
        studentQuestionsDetails = lstQLQuestionAttemptDetails.filter(**filterSQues).all()
        if studentQuestionsDetails and studentQuestionsDetails.count() > 0 :
            sameqs = []
            for qlqd in studentQuestionsDetails :
                filterQues = {  "QuestionId" : qlqd.QuestionId }
                quesMasterLst = lstQLMasterQ.filter(**filterQues).all()
                quesMaster = quesMasterLst[0]
                if ObjectExistInArray(qlSRV.QuestionsDetails,"Id", qlqd.QuestionId) is False:
                    question = Classes.RevelQuestionMasterForStudentReport()
                    question.Id = qlqd.QuestionId.encode("utf-8")   
                    question.OptionAlignment = "V"
                    if quesMaster.AdditionalInfo is not None and quesMaster.AdditionalInfo != '""' and quesMaster.AdditionalInfo != '' and quesMaster.AdditionalInfo != '{}':
                        jsonObjDetail = literal_eval(quesMaster.AdditionalInfo)
                        question.OptionAlignment = str(jsonObjDetail["OptionAlignment"])
                    
                    question.Text = quesMaster.QuestionText.replace("Select an option from the choices below and click Submit.","")
                    
                    lstqloption = [] # List<QlOption>()
                    if quesMaster.Options != "" and quesMaster.Options != '[""]' and quesMaster.Options != '[]' :
                        try :
                            lstqloption = literal_eval(quesMaster.Options)
                        except Exception :
                            pass
                        question.Options = lstqloption
                                        
                    question.OccurenceNo = ""

                    if quesMaster.QuestionTitle is not None :
                        question.QuestionTitle = quesMaster.QuestionTitle.encode("utf-8")
                        # same question occurance no
                        filtersmq = { 'templateId' : templateId, 'QuestionTitle' : question.QuestionTitle }
                        if revelM.RevelMasterQuestions.objects.filter(**filtersmq).count() > 1 :
                            supval = ""
                            occrnc = sameqs.count(question.QuestionTitle) + 1
                            question.OccurenceNo = str(occrnc)
                        
                            if occrnc == 1 :
                                supval = "<sup>st</sup>"
                            elif occrnc == 2 :
                                supval = "<sup>nd</sup>"
                            elif occrnc == 3 :
                                supval = "<sup>rd</sup>"
                            else :
                                supval = "<sup>th</sup>"                            
                        
                            question.OccurenceNo = " (" + question.OccurenceNo + supval + " instance)"
                            sameqs.append(question.QuestionTitle)
                        # if end question occ more that once
                    # end if qlqd.QuestionTitle is not None 
                    qlSRV.QuestionsDetails.append(question)
                # if end ObjectExistInArray
                qlquestion = Classes.RevelQuestionForStudentReport()
                qlquestion.Id = qlqd.QuestionId
                qlquestion.PointsObtained = int(qlqd.Points)
                qlquestion.TotalPoints = int(quesMaster.TotalPoints)
                qlquestion.SelectedOption = qlqd.SelOptionId
                
                if int(qlqd.Points) >= 5 :
                    qlquestion.PointsImage = k_ANALYTICS_STATIC + "images/5point.png"
                else :
                    qlquestion.PointsImage = k_ANALYTICS_STATIC + "images/" + str(qlquestion.PointsObtained) + "point.png"
                
                student.Questions.append(qlquestion)
            # endfor qlqd in studentQuestionsDetails :
            
        qlSRV.Results.append(student)
           
    # endfor qlMa in qlMasterAttempts :     
    
    if qlSRV.Results.__len__() > 0:
        filterscr = {"CompletionStatus" : "complete" , "Score__isnull" : False }
        scorelist = qlMasterAttempts.filter(**filterscr).values("Score").all()
        if scorelist.count() > 0 :
            #print scorelist
            qlSRV.AverageScore = qlMasterAttempts.filter(**filterscr).aggregate(Avg('Score'))["Score__avg"]
        else :
            qlSRV.AverageScore = 0        
    else :
        qlSRV.AverageScore = 0
                    
    return qlSRV
 
def GetQuestionDetailsModel(templateId, courseId, ASGN = "" , isStudentDetails = False) :
    #Anu 14-nov-2017 module and structure renamed changes
    
    #'unicode-escape' is used to escape sequences in string
    templateId = templateId.decode('unicode-escape')
    
    filter1 = {"templateId": templateId, "courseId": courseId}
    lstQLMasterQ = revelM.RevelMasterQuestions.objects.filter(**filter1).all()
    packagerelPath = getOptionPath(templateId)    
    if (packagerelPath.find('/qualsims') != -1):
        packagerelPath = packagerelPath.replace('/qualsims', 'qualsims')        
        
    filter2 = {"templateId": templateId, "courseId": courseId, 'ReportStatus' : 'active'}
    qlMasterAttempts = None
    
    if ASGN :
        filter2["assignmentId"] = ASGN 
        qlMasterAttempts = revelM.RevelMasterAttemptData.objects.filter(**filter2)
    else :
        qlMasterAttempts = revelM.RevelMasterAttemptData.objects.filter(**filter2)
    
    if qlMasterAttempts.count() == 0 :
        return " No data found"
     
    lstQLMasterAttemptsId = qlMasterAttempts.values_list("Id")
    
    filter3 = {'MstAttemptId__in' :lstQLMasterAttemptsId }
    lstQLQuestionAttemptDetails = revelM.RevelQuestionAttemptDetails.objects.filter(**filter3).all()
    
    sameqs = []
    
    qlQDRV = Classes.RevelQuestionDetailReportView()
    qlQDRV.Results = []
    
    for qlMqd in lstQLMasterQ :
        qlQDR = Classes.RevelQuestionDetailReport()
        
        if qlMqd.QuestionText is not None :
            qlQDR.Text = qlMqd.QuestionText.encode("utf-8")
        
        qlQDR.Id = qlMqd.QuestionId
        qlQDR.OccurenceNo = ""
        
        if qlMqd.QuestionTitle is not None :
            qlQDR.QuestionTitle = qlMqd.QuestionTitle.encode("utf-8")
            # same question occurance no
            filtersmq = { 'templateId' : templateId, 'QuestionTitle' : qlQDR.QuestionTitle }
            if revelM.RevelMasterQuestions.objects.filter(**filtersmq).count() > 1 :
                supval = ""
                occrnc = sameqs.count(qlQDR.QuestionTitle) + 1
                qlQDR.OccurenceNo = str(occrnc)
                
                if occrnc == 1 :
                    supval = "<sup>st</sup>"
                elif occrnc == 2 :
                    supval = "<sup>nd</sup>"
                elif occrnc == 3 :
                    supval = "<sup>rd</sup>"
                else :
                    supval = "<sup>th</sup>"                            
                            
                qlQDR.OccurenceNo = " (" + qlQDR.OccurenceNo + supval + " instance)"
                sameqs.append(qlQDR.QuestionTitle)
        
        qlQDR.Points = str(int(qlMqd.TotalPoints))
        qlQDR.Options = []
        qlQDR.OptionAlignment = "V"
                
        if qlMqd.AdditionalInfo is not None and qlMqd.AdditionalInfo != '""' :            
            qlQDR.OptionAlignment = "V" 
            #str(jsonObjDetail["OptionAlignment"])
        # end if qlMqd.AdditionalInfo
        
        filter4 = {"QuestionId": qlMqd.QuestionId }
        lstattemptedforQuestion = lstQLQuestionAttemptDetails.filter(**filter4)        
        lstattemptedforQuestionId = lstQLQuestionAttemptDetails.values("MstAttemptId").distinct()
        
        if isStudentDetails :
            qlQDR.Students = []
            filterstd = {'Id__in' : lstattemptedforQuestionId }
            lstMasterQsnAttempt = qlMasterAttempts.filter(**filterstd).all()
            for qma in lstMasterQsnAttempt :            
                student = Classes.RevelStudentDetails()                
                student.Name = qma.StudentName
                student.Id = qma.Student_Id
                student.MasterAttemptId = qma.Id
                filterques = {'MstAttemptId' : qma.Id , 'QuestionId' : qlMqd.QuestionId}
                #print lstattemptedforQuestion.count()
                if lstattemptedforQuestion.count() > 0 :                
                    studentQAttempt = lstattemptedforQuestion.filter(**filterques).values_list("Points").all()                                        
                    if studentQAttempt :
                        #print studentQAttempt
                        student.Points = str(int(studentQAttempt[0][0]))
                        qlQDR.Students.append(student)                    
        #end if isStudentDetails 
        
        #no of times question answered
        qlQDR.NumberOfTimesAnswered = lstattemptedforQuestion.count()
        qlQDR.QuestionAttempted = str(qlQDR.NumberOfTimesAnswered)
        
        #no of time question attempted
        ttlAttmpt = lstQLMasterAttemptsId.count()
        qlQDR.TotalAttempted = str(ttlAttmpt)
        
        if ttlAttmpt > 0 :              
            qlQDR.Presented = str(int(float(qlQDR.NumberOfTimesAnswered) / float(ttlAttmpt) * 100)) + "%"    
        else :
            qlQDR.Presented = "0" + "%"
                            
        if qlQDR.NumberOfTimesAnswered > 0 :            
            avgscr = lstattemptedforQuestion.aggregate(Avg('Score'))
            if avgscr.__len__() > 0 :
                qlQDR.AverageScorePercent = str(int(avgscr["Score__avg"]))
            else :
                qlQDR.AverageScorePercent = "0"
        else:
            qlQDR.AverageScorePercent = "0"                
                
        lstqloption = []
        correctCnt = 0 
        incorrectCnt = 0
        partialCorrCnt = 0
        
        if qlMqd.Options == "" or qlMqd.Options == '[""]' or qlMqd.Options == '[]' :
            pass
        else :
            try :
                lstqloption = literal_eval(qlMqd.Options)
            except Exception :
                pass
            
            for qloption in lstqloption :
                qlOptionReport = Classes.RevelOptionReport()
                try:
                    qlOptionReport.Text = qloption["Text"]
                except Exception as ine:
                    qlOptionReport.Text = ''
                    
                try:    
                    qlOptionReport.Status= qloption["Status"]
                except Exception as ine:
                    qlOptionReport.Status= ''
                    
                try:                   
                    qlOptionReport.Points = qloption["Points"]   
                except Exception as ine:
                    qlOptionReport.Points = "0"
                 
                try:                 
                    qlOptionReport.Image = packagerelPath + "/" + qloption["Img"] 
                except Exception as ine:
                    qlOptionReport.Image = ""       
                
                #print qloption["Points"]
                seloptid = ""
                try: 
                    seloptid = qloption["Id"]
                except Exception as ine:
                    seloptid = ""
                    
                filter5 = {"SelOptionId": seloptid}
                qlOptionReport.NumberOfTimesAnswered = lstattemptedforQuestion.filter(**filter5).count()
                
                percent = 0
                if qlOptionReport.NumberOfTimesAnswered > 0:
                    percent = (float(qlOptionReport.NumberOfTimesAnswered) / float(qlQDR.NumberOfTimesAnswered) )* 100
                
                if percent > 0 :
                    qlOptionReport.Percent = str(round(percent,2)) + "%"
                
                if qlOptionReport.Status.lower() == "correct" and qlOptionReport.NumberOfTimesAnswered > 0 :
                    correctCnt +=1
                    
                if qlOptionReport.Status.lower() == "incorrect" and qlOptionReport.NumberOfTimesAnswered > 0 :
                    incorrectCnt +=1
                    
                if qlOptionReport.Status.lower() == "partial" and qlOptionReport.NumberOfTimesAnswered > 0 :
                    partialCorrCnt +=1
                
#                 basePath = ""
#                 if qlOptionReport.Image :
#                     splitarr = qlOptionReport.Image.split('/')
#                     if splitarr != None and splitarr.length() == 0 :
#                         basePath = "/assets/115/images/" 
#                     else :
#                         basePath = qlOptionReport.Image.Replace(splitarr[splitarr.Length - 1], "")
                                         
                if qlOptionReport.Points >= 5 :
                    qlOptionReport.PointsImage = k_ANALYTICS_STATIC + "images/5point.png"
                else :
                    qlOptionReport.PointsImage = k_ANALYTICS_STATIC + "images/" + str(qlOptionReport.Points) + "point.png" 
                            
                qlQDR.Options.append(qlOptionReport) 
        #for qloption in lstqloption ends
        
        #question graph
        qlQDR.ForGraph = str(qlQDR.NumberOfTimesAnswered) + "###" + str(correctCnt) + "###" + str(incorrectCnt) + "###" + str(partialCorrCnt)
         
        qlQDRV.Results.append(qlQDR)
    #for qlMqd in lstQLMasterQ : ends
    
    if qlQDRV.Results.__len__() > 0:
                
        totalattempts = qlMasterAttempts.count()
        
        filterComp = {"CompletionStatus" : "complete"}
        totalcompleted = qlMasterAttempts.filter(**filterComp).count()
        #print " totalcompleted " + str(totalcompleted )
        compltcnt = 0
        if totalattempts > 0 :
            compltcnt = int(float(totalcompleted) / float(totalattempts) * 100)
                    
        qlQDRV.AverageCompleted = float(compltcnt)
        #print " compltcnt " + str(compltcnt )
        
                
        filterscr = {"CompletionStatus" : "complete" , "Score__isnull" : False }
        scorelist = qlMasterAttempts.filter(**filterscr).values("Score").all()
        if scorelist.count() > 0 :
            #print scorelist
            qlQDRV.AverageScore = qlMasterAttempts.filter(**filterscr).aggregate(Avg('Score'))["Score__avg"]
            qlQDRV.MedianScore = getMedian(scorelist)
        else :
            qlQDRV.AverageScore = 0
            qlQDRV.MedianScore = 0
    else :
        qlQDRV.AverageScore = 0
        qlQDRV.MedianScore = 0
        qlQDRV.AverageCompleted = 0
    return qlQDRV




@csrf_exempt
def RevelResultReport(request):    
    templateId = request.GET.get('templateId', None)
    ASGN = request.GET.get('ASGN', None)
    courseId = request.GET.get('Course_Id', '')
    stuID = request.GET.get('STUId', '')
    
    
    queryParam = {"templateId" : templateId , "courseId" : courseId, "assignmentId" : ASGN, "studentId": stuID} 
    qlQDRV = RevelResultReportModel(templateId, courseId, ASGN, stuID)
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('RevelResultReport.html', { "Status" : "No data found" }, context_instance = context)
    
    urlOrigin = "https://" + request.META.get("HTTP_HOST")
    #new file 25/11/17 2:48pm
    r = requests.get(urlOrigin + '/content/revelsims/commonfiles/template_mappings.json')
    if r.status_code == 200:
        template_mappings = r.json()
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'RRView': qlQDRV , 'queryParam' : queryParam, 'TemplateURL': urlOrigin + template_mappings[templateId]}
 
    return render_to_response('RevelResultReport.html', context_dict, context_instance = context)


def RevelResultReportModel(templateId, courseId, ASGN = "", stdId="") :
    templateId = templateId.decode('unicode-escape')
    
    filter2 = {"templateId" : templateId , "courseId" : courseId, 'CompletionStatus' : 'complete'}
    if stdId!="":
        filter2 = {"templateId" : templateId , "courseId" : courseId, "Student_Id": stdId,  'CompletionStatus' : 'complete'}
    qlMasterAttempts = None
    
    if ASGN :
        filter2["assignmentId"] = ASGN 
        qlMasterAttempts = revelM.RevelMasterAttemptData.objects.filter(**filter2).values('Student_Id','StudentName','StartDate','EndDate','Score').order_by('Student_Id','StartDate').all()
    else :
        qlMasterAttempts = revelM.RevelMasterAttemptData.objects.filter(**filter2).values('Student_Id','StudentName','StartDate','EndDate','Score').order_by('Student_Id','StartDate').all()
    
    
    if qlMasterAttempts.count() == 0 :
        return "No data found"    
    
    #    stdLst = qlMasterAttempts.distinct('Student_Id','StudentName').all()                

    return qlMasterAttempts #{ 'qlLst' : qlMasterAttempts, 'stdLst' :stdLst } 




def getMedian(numericValues):
    theValues = sorted(numericValues)
    if len(theValues) % 2 == 1:
        #print theValues[(len(theValues))/2]["Score"] 
        return theValues[(len(theValues))/2]["Score"] 
    else:
        lower = theValues[len(theValues)/2-1]
        upper = theValues[len(theValues)/2]
        #(float(lower["Score"] + upper["Score"])) / 2
        return (float(lower["Score"] + upper["Score"])) / 2  


def ObjectExistInArray(arr, prop, val) :
    if len(arr) > 0 :        
        for ob in arr :
            if ob.Id == val :
                return True            
    return False


def getOptionPath(qlid):
    pkgPath = ''
    if (qlid.find('qualsims') != -1):
        pkgPath = qlid.replace('/armstrong','').replace('/kotler','').replace('/solomon','')
        pkgPath = pkgPath.replace('/ebert','').replace('/bovee','')
        pkgPath = pkgPath.replace('/certo','').replace('/robbins10 Simulation','').replace('/robbins10','').replace('/robbins14','').replace('/robbins17','').replace('/wheelen','')
        pkgPath = pkgPath.replace('/david','').replace('/barringer','').replace('/dressler','').replace('/mariotti','').replace('/scarborough','')
        pkgPath = pkgPath.replace('/cheeseman','').replace('/robbins8e', '').replace('/gibson10e', '')
        pkgPath = pkgPath.replace('-', '_')
        pkgPath = pkgPath.replace('/qualsims', 'qualsims')                
    
    return pkgPath

@csrf_exempt
def sendemail(request):
    from_addr    = 'no-reply@3psmedia.com', 
    to_addr_list = ['vinod@knowdl.com'],
    cc_addr_list = ['anuja@knowdl.com'], 
    subject      = 'Hi from Vinod', 
    message      = 'test email from python', 
    login        = 'no-reply@3psmedia.com'
    password     = '3ps!2345'

    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems





        
        






















