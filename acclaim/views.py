'''
Created on Apr 13, 2017
updated on Oct 27, 2017
@author: anuja
'''
#from testKnowdl import models as revelM
from django.shortcuts import render_to_response
from django.template import RequestContext 
import django
import requests
from django.http import HttpResponse
import json
import base64
import datetime
#from datetime import datetime
from pytz import timezone

from django.views.decorators.csrf import csrf_exempt

#Anu 25-oct-2017 for QLInteractionController
def DummyPage(request):
    
    print django.get_version()
    return render_to_response('NewFile.html')


@csrf_exempt
def showpage(request):
    pagedata = request.POST.get('pagehtml', "<h1>1). No data received now.</h1>")
    import HTMLParser
    htmlParser = HTMLParser.HTMLParser()
    return HttpResponse(htmlParser.unescape(pagedata), status=200, content_type="text/html")

def RevelResultReport(request):    
    templateId = request.GET.get('templateId', None)
    ASGN = request.GET.get('ASGN', None)
    courseId = request.GET.get('Course_Id', '')
    
    queryParam = {"templateId" : templateId , "courseId" : courseId, "assignmentId" : ASGN} 
    qlQDRV = RevelResultReportModel(templateId, courseId, ASGN)
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('RevelResultReport.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'RRView': qlQDRV , 'queryParam' : queryParam}
 
    return render_to_response('RevelResultReport.html', context_dict, context_instance = context)


def RevelResultReportModel(templateId, courseId, ASGN = "") :
    templateId = templateId.decode('unicode-escape')
    
    filter2 = {"templateId" : templateId , "courseId" : courseId, 'CompletionStatus' : 'complete'}
    qlMasterAttempts = None
    
    if ASGN :
        filter2["assignmentId"] = ASGN 
        qlMasterAttempts = revelM.RevelMasterAttemptData.objects.filter(**filter2).values('Student_Id','StudentName','StartDate','EndDate','Score').order_by('-StartDate').all()
    else :
        qlMasterAttempts = revelM.RevelMasterAttemptData.objects.filter(**filter2).values('Student_Id','StudentName','StartDate','EndDate','Score').order_by('-StartDate').all()
    
    
    if qlMasterAttempts.count() == 0 :
        return "No data found"    
    
    #    stdLst = qlMasterAttempts.distinct('Student_Id','StudentName').all()                

    return qlMasterAttempts #{ 'qlLst' : qlMasterAttempts, 'stdLst' :stdLst } 

# working
def getBadgeTemplates(request):
    try :
        ktoken = "E6ex7WQPgiRDkFmjdC9vx_99HOcK8e4Ybs71OhMj"
        ktoken64 = base64.b64encode(ktoken)
        str1 = 'Basic ' + ktoken64
        url = 'https://sandbox-api.youracclaim.com/v1/organizations/a2225ab0-656d-4b9a-ba92-e1834546d060/badge_templates.json'
        data = {'name' :"Fencing Club Champion" , 'description' :"The earner of this badge won the fencing club championship." ,
                'template_type' :"Skill"}
        headers = {'Accept': 'application/json', 'Authorization' : str1 , 'Content-Type': 'application/json', 'Content-Length' : '42' }
        
        r = requests.get(url, data=json.dumps(data), headers=headers)    
        
        #if r.status_code == 200:
        return HttpResponse(r.status_code + "-------" + r.text)
    except Exception as e :
            return HttpResponse(e)
        
# working        
def getOrgTokens(request):    
    try :
        url = 'https://sandbox-api.youracclaim.com/v1/organizations/a2225ab0-656d-4b9a-ba92-e1834546d060/authorization_tokens'        
        ktoken = "E6ex7WQPgiRDkFmjdC9vx_99HOcK8e4Ybs71OhMj"
        ktoken64 = base64.b64encode(ktoken)
        str1 = 'Basic ' + ktoken64       
        headers = {'Authorization' : str1 }
        
        r = requests.get(url,   headers=headers)    
        
        #if r.status_code == 200:
        return HttpResponse(r.status_code + "-------" + r.text)
    except Exception as e :
            return HttpResponse(e)
    
def issueBadgeToUser(request):
    try:
        ktoken = "E6ex7WQPgiRDkFmjdC9vx_99HOcK8e4Ybs71OhMj"
        ktoken64 = base64.b64encode(ktoken)
        str1 = 'Basic ' + ktoken64
        url = 'https://sandbox-api.youracclaim.com/v1/organizations/a2225ab0-656d-4b9a-ba92-e1834546d060/badges'
        data = {
              "recipient_email":  request.GET.get('issueto', 'vinod@knowdl.com'),
              "user_id": "01d5b774-73d3-46ca-937e-828bc68bde87",# remaining
              "badge_template_id": "d05f400d-cd77-41e0-bd4f-b34be9ffa755",
              "issued_at": datetime.datetime.now(timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S %z"),
              "issued_to_first_name": request.GET.get('fname', 'vinod@knowdl.com'),
              "issued_to_last_name": request.GET.get('lname', 'vinod@knowdl.com'),              
              #"issuer_earner_id": "abc123",
              "locale": "en"              
            }
        headers = {'Accept': 'application/json', 'Authorization' : str1 , 'Content-Type': 'application/json', 'Content-Length' : '42' }
        
        r = requests.post(url, data=json.dumps(data), headers=headers)    
        
        #if r.status_code == 200:
        return HttpResponse(str(r.status_code) + "-------" + r.text)
    except Exception as e:
        return HttpResponse(e)

def getOrganization(request):
    try:
        ktoken = "E6ex7WQPgiRDkFmjdC9vx_99HOcK8e4Ybs71OhMj"
        ktoken64 = base64.b64encode(ktoken)
        str1 = 'Basic ' + ktoken64
        url = 'https://sandbox-api.youracclaim.com/v1/organizations/a2225ab0-656d-4b9a-ba92-e1834546d060'
        headers = { 'Authorization' : str1 }
        
        r = requests.get(url, headers=headers)    
        
        if r.status_code == 200:
            return HttpResponse(r.text)
    except Exception as e:
        return HttpResponse(e)
    

def getIssuers(request):
    try:
        ktoken = "E6ex7WQPgiRDkFmjdC9vx_99HOcK8e4Ybs71OhMj"
        ktoken64 = base64.b64encode(ktoken)
        str1 = 'Basic ' + ktoken64
        url = 'https://sandbox-api.youracclaim.com/v1/organizations/a2225ab0-656d-4b9a-ba92-e1834546d060/issuers'
        headers = { 'Authorization' : str1 }
        
        r = requests.get(url, headers=headers)    
        
        #if r.status_code == 200:
        return HttpResponse(str(r.status_code) + "-------" + r.text)
    except Exception as e:
        return HttpResponse(e)

    

def getgrantors(request):
    try:
        ktoken = "E6ex7WQPgiRDkFmjdC9vx_99HOcK8e4Ybs71OhMj"
        ktoken64 = base64.b64encode(ktoken)
        str1 = 'Basic ' + ktoken64
        url = 'https://sandbox-api.youracclaim.com/v1/organizations/a2225ab0-656d-4b9a-ba92-e1834546d060/grantors'
        headers = { 'Authorization' : str1 }
        
        r = requests.get(url, headers=headers)    
        
        #if r.status_code == 200:
        return HttpResponse(r.status_code + "-------" + r.text)
    except Exception as e:
        return HttpResponse(e)

def getSelfInfo(request):    
    try:
        ktoken = "E6ex7WQPgiRDkFmjdC9vx_99HOcK8e4Ybs71OhMj"
        ktoken64 = base64.b64encode(ktoken)
        str1 = 'Basic ' + ktoken64
        url = 'https://youracclaim.com/oauth/v1/users/self'
        headers = { 'Authorization' : str1 }
        
        r = requests.get(url, headers=headers)    
        
        #if r.status_code == 200:
        return HttpResponse(str(r.status_code) + "-------" + r.text)
    except Exception as e:
        return HttpResponse(e)
        

def sendemail(request):
    import smtplib
    from_addr    = 'no-reply@3psmedia.com'
    to_addr_list = ['vinod@knowdl.com']
    cc_addr_list = ['anuja@knowdl.com']
    subject      = 'Hi from Vinod'
    message      = 'test email from python'
    login        = 'no-reply@3psmedia.com'
    password     = '3ps!2345'

    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return HttpResponse("---Success----" )

