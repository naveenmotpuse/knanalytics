


'''
Created on Apr 13, 2017
updated on Oct 25, 2017
@author: anuja
'''
from knowdlanalytics import models as m, Classes
from django.shortcuts import render_to_response
from django.template import RequestContext
from __builtin__ import str, int
import knowdlanalytics.CommonRoutines as ComnFunc
from django.http import HttpResponse
from ast import literal_eval
from django.db.models import Avg
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from econ.utils import CorsHttpDecorator
import json
from decimal import Decimal


k_ANALYTICS_STATIC = '/econservice-static/knowdlanalytics/'

#Anu 25-oct-2017 for QLInteractionController
def DummyPage(request):
    returnResponse = "we can call method this way"    
    context = RequestContext(request)  
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Message' : returnResponse } 
    return render_to_response('NewFile.html', context_dict, context_instance = context)

@csrf_exempt
@CorsHttpDecorator
def QLInteractionProcess(request):    
    returnResponse = "call method this way "
    command = ""
    jsondatavalues = ""
    try :
        jsondatavalues = json.loads(request.POST.get('jsondata', None))
        command = request.POST.get('command', None)                
        #if "AssignmentLocation" in jsondatavalues :
        #    AssignmentLocation = jsondatavalues["AssignmentLocation"]
        #elif "LOC" in jsondatavalues :
        #    AssignmentLocation = jsondatavalues["LOC"]
            
        #if ComnFunc.IsValidRequest(AssignmentLocation) :
        if command == "launch" :
            returnResponse = fPostAssignmentData(jsondatavalues, "")             
        elif command == "updateattemptdata" :
            returnResponse = fPostAttemptData(jsondatavalues, "")            
        elif command == "classaverage" :
            returnResponse = fGetClassAverage(jsondatavalues, "")
            
    except Exception as e :
            #DBLog("QL Interaction Error: Command=" + command + ", jsondata=" + "", e);
            returnResponse = str(e)
                                        
    return HttpResponse(returnResponse)

def fPostAttemptData(jsondatavalues, location) :
    returnValue = "Begin 111 fPostAttemptData:"
    assignmentId , qlId , studentId , completionStatus = "","","",""
    overallScore = 0.0
    overallTimeSpent= 0.0
    overallPoints = 0.0
    
    try :
        if "Assignment_Id" in jsondatavalues :
            assignmentId = jsondatavalues["Assignment_Id"]
            
        if "QL_Id" in jsondatavalues :
            qlId = jsondatavalues["QL_Id"]
                
        if "Student_Id" in jsondatavalues :
            studentId= jsondatavalues["Student_Id"]
            
        if "CompletionStatus" in jsondatavalues :
            completionStatus = jsondatavalues["CompletionStatus"] 
            
        if "OverallScore" in jsondatavalues :
            overallScore = Decimal(str(jsondatavalues["OverallScore"])) 
        
        if "OverallTimeSpent" in jsondatavalues :
            overallTimeSpent = Decimal(str(jsondatavalues["OverallTimeSpent"])) 
        
        if "OverallPoints" in jsondatavalues :
            overallPoints = Decimal(str(jsondatavalues["OverallPoints"])) 
        
        #enter assignment details on launch if details are not present    
        filter1 = {"Assignment_Id": assignmentId,"QL_Id": qlId, "Student_Id" :studentId, "CompletionStatus" : "inprogress" }
        
        qlma = None
        try:
            qlma =  m.ql_masterattempts.objects.get(**filter1)
        except Exception as e :
            returnValue = returnValue + "Error" + str(e)
            qlma = None
                  
        maxscore = 0.0
        
        filterMaxScr = {"Assignment_Id": assignmentId,"QL_Id": qlId, "Student_Id" :studentId, "ReportStatus" : "active", "CompletionStatus":"complete" }        
        
        qlmaMaxScr = m.ql_masterattempts.objects.filter(**filterMaxScr).count()
        

        try:
            if qlmaMaxScr > 0 :
                maxscorelist = m.ql_masterattempts.objects.filter(**filterMaxScr).values_list("Score",flat=True)            
                if maxscorelist is not None and len(maxscorelist)>0:
                    maxscore = maxscorelist[0]
            
            
        except Exception as e:
            returnValue = returnValue + "Error" + str(e)            
        
        if maxscore is None:
            maxscore = 0.0
            
        returnValue = returnValue + "-maxscore:" + str(maxscore) + "overallScore:" + str(overallScore)
                          
        if qlma is not None :
            #update master attempt
            if overallScore is None:
                overallScore = 0.0
                
            qlma.Score = overallScore
            qlma.Points = overallPoints
            if overallTimeSpent != 0 :
                qlma.TimeSpent = overallTimeSpent
                
            returnValue = returnValue + "completionStatus:" + str(completionStatus) 
              
            if completionStatus != "" and completionStatus.lower() == "complete" :
                qlma.CompletionStatus = completionStatus.lower()
                returnValue = returnValue + "-qlma.Score:" + str(qlma.Score)
                if qlma.Score is not None and maxscore < qlma.Score:                        
                    qlma.ReportStatus = "active"
                    scorediff = Decimal(str(qlma.Score)) - Decimal(str(maxscore))
                    filter23 = {"Assignment_Id": assignmentId, "AdditionalField1": qlId}
                    try:
                        qlassigadddeta = m.ql_assignmentadditionaldetails.objects.get(**filter23)
                        returnValue = returnValue + "TotalScore:" + str(qlassigadddeta.TotalScore)  + "-scorediff:" + str(scorediff) 
                        qlassigadddeta.TotalScore = qlassigadddeta.TotalScore + scorediff
                        returnValue = returnValue + "after sum - TotalScore:" + str(qlassigadddeta.TotalScore)   
                        qlassigadddeta.save()
                    except Exception as innr:
                        returnValue = returnValue + "TotalScore update Error:" + str(innr)  
                        
                    
                qlma.EndDate = datetime.now()
                qlma.AssignmentLocation = ""
                qlma.save()
                #Update other attempts                    
                if qlma.ReportStatus == "active" :
                    filterRStat = {"Assignment_Id": assignmentId,"QL_Id": qlId, "Student_Id" :studentId }
                    m.ql_masterattempts.objects.filter(**filterRStat).exclude(Id = qlma.Id).update(ReportStatus = "inactive")
             
            addquesdetail = AddQuestionDetails(qlma,jsondatavalues)            
            returnValue = returnValue + addquesdetail
            
        returnValue = returnValue + " - Update Attempt Data Success"
    except Exception as e :
            #DBLog("QL Interaction Error: Command=postAttemptData jsondata=" + "", e);
            returnValue = returnValue + str(e) 
            
    return returnValue

def AddQuestionDetails(qlma, jsondatavalues):
    retval = 'Begin 111 AddQuestionDetails:'
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
        
    if qId is not None and qId != "" and qlma is not  None :
        try:
            filterQMQ = {"QL_Id" : qlma.QL_Id ,"QuestionId" : qId ,"PageId" : pId}
            
            qlmq = None
            try:
                qlmq = m.ql_masterquestions.objects.get(**filterQMQ)  
            except Exception as e:
                qlmq = None  
                retval = retval + " Error:" + str(e)                    
                      
            if qlmq is not None:                
                qlmq.QuestionText = qText
                qlmq.Options = str(qOptions)
                qlmq.QuestionTitle = qTitle
                qlmq.TotalPoints = qTotal            
                qlmq.AdditionalInfo = str(q_mqAdditionalInfo) 
                qlmq.save()                
            else :
                qlmq = m.ql_masterquestions.objects.create(QL_Id = qlma.QL_Id,PageId = pId,QuestionId = qId,QuestionText = qText,TotalPoints = qTotal,Options = qOptions,QuestionTitle = qTitle,
                            Type = qtype,AdditionalInfo = str(q_mqAdditionalInfo))                
                
            
            '''Create User's question attempt entry.
            '''
            filterQAtmpt = {"MstAttemptId" : qlma.Id, "PageId" : pId , "QuestionId": qId}
            
            qlqad = None
            try:
                qlqad = m.ql_questionattemptdetails.objects.get(**filterQAtmpt)
            except Exception as e:
                qlqad = None
                retval = retval + " Error:" + str(e)
            
            if qlqad is not None:  
                retval = retval + "update question details:"           
                qlqad.CorrectStatus = qCorrectStatus
                qlqad.TimeSpent = qTimespent
                qlqad.Score = qScore
                qlqad.Points = qPoints
                qlqad.SelOptionId = qSelOptionId
                qlqad.AdditionalInfo = str(qAdditionalInfo)
                qlqad.save()  
                retval = retval + "update question details complete:"                
            else :
                retval = retval + "Create question details:" 
                qlqad = m.ql_questionattemptdetails.objects.create(MstAttemptId = qlma.Id,PageId = pId,QuestionId = qId,CorrectStatus = qCorrectStatus,TimeSpent = qTimespent,Score = qScore,Points = qPoints,SelOptionId = qSelOptionId,AdditionalInfo = str(qAdditionalInfo))
                retval = retval + "Create question details complete:"
        except Exception as ine:
            retval = retval + "ql_questionattemptdetails create_update Error:" + str(ine)
            
    return retval

def fGetClassAverage(jsondatavalues, loc) :
    returnValue =""
    try :
        assignmentId , qlId , loc  = "","",""        
        if "Assignment_Id" in jsondatavalues :
            assignmentId = jsondatavalues["Assignment_Id"]
                
        if "QL_Id" in jsondatavalues :
            qlId = jsondatavalues["QL_Id"]            
        
        try :
            filterAvg = {"Assignment_Id": assignmentId,"AdditionalField1": qlId}
            qlAssignmentAvg = m.ql_assignmentadditionaldetails.objects.filter(**filterAvg).values("TotalScore","NumOfUsers").all()
            if qlAssignmentAvg.count() > 0 and  Decimal(str(qlAssignmentAvg[0]["NumOfUsers"])) > 0 :
                returnValue = Decimal(str(qlAssignmentAvg[0]["TotalScore"]))/Decimal(str(qlAssignmentAvg[0]["NumOfUsers"]))
            
        except Exception as excp :
            returnValue = ""
  
        if returnValue == "" :
            filterMaxScr = {"Assignment_Id": assignmentId,"QL_Id": qlId, "ReportStatus" : "active" }        
            avgscore = m.ql_masterattempts.objects.filter(**filterMaxScr).aggregate(Avg('Score'))        
            try:            
                returnValue = str(round(avgscore["Score__avg"] , 2))
            except Exception as inr:            
                returnValue = str(0.0)
                  
    except Exception as e :
            #DBLog("QL Interaction Error: Command=GetClassAverage jsondata=" + "", e);
            returnValue = str(e)
            
    return returnValue         


def fPostAssignmentData(jsondatavalues, location) :
    returnValue = "Begin 111 fPostAssignmentData:"
    
    assignmentId , qlTitle , qlId , studentId , sessionId , assignmentTitle ,studentName , role  , objectiveDetails = "","","","","","","","",""
    numberOfAttempts =0 
    targetPoints = 0.0
    
    try :
        if "Assignment_Id" in jsondatavalues :
            assignmentId = jsondatavalues["Assignment_Id"]
            
        if "QLTitle" in jsondatavalues :
            qlTitle = jsondatavalues["QLTitle"]
        
        if "QL_Id" in jsondatavalues :
            qlId = jsondatavalues["QL_Id"]
                
        if "Student_Id" in jsondatavalues :
            studentId= jsondatavalues["Student_Id"]
            
        if "Session_Id" in jsondatavalues :
            sessionId = jsondatavalues["Session_Id"]
    
        if "AssignmentTitle" in jsondatavalues :
            assignmentTitle= jsondatavalues["AssignmentTitle"]
    
        if "NumberOfAttempts" in jsondatavalues :
            numberOfAttempts = int(str(jsondatavalues["NumberOfAttempts"])) #int ??
    
        if "TargetPoints" in jsondatavalues :
            targetPoints = float(str(jsondatavalues["TargetPoints"])) #double ??
            
        if "StudentName" in jsondatavalues :
            studentName = jsondatavalues["StudentName"] 
    
        if "Role" in jsondatavalues :
            role = jsondatavalues["Role"] 
            
        if "ObjectiveDetails" in jsondatavalues :
            objectiveDetails = jsondatavalues["ObjectiveDetails"]             
    
        #enter assignment details on launch if details are not present    
        filter1 = {"Assignment_Id": assignmentId,"QL_Id": qlId}
        diad = None
        try:
            diad = m.ql_assignmentdetails.objects.get(**filter1)
        except Exception as e:
            diad = None
            
        returnValue = returnValue + "abc Id:"
                           
        if diad is not None:
            returnValue = returnValue + "efgttt Id:"            
            diad.AssignmentTitle = assignmentTitle
            diad.NumberOfAttempts = numberOfAttempts                    
            diad.ObjectiveDetails = str(objectiveDetails)
            diad.save()
            
            returnValue = returnValue + "efg Id:"
        else :  
            returnValue = returnValue + "efgggg Id:"      
            diad = m.ql_assignmentdetails.objects.create(Assignment_Id = assignmentId,QL_Id = qlId,NumberOfAttempts = numberOfAttempts,TargetPoints = targetPoints,
            QLTitle = qlTitle,AssignmentTitle = assignmentTitle,Status = True,ObjectiveDetails = str(objectiveDetails))
            
            returnValue = returnValue + "create ql_assignmentadditionaldetails:"    
            assadddet = m.ql_assignmentadditionaldetails.objects.create(Assignment_Id = assignmentId, AdditionalField1 = qlId, TotalScore = 0, NumOfUsers = 0,  AdditionalField2 ="", AdditionalField3="")
            returnValue = returnValue + "after create ql_assignmentadditionaldetails:"  + str(assadddet.Id) 
            
            
           
        filter1['Student_Id'] = studentId  
        returnValue = returnValue + "hij Id:"  
        attemCount = m.ql_masterattempts.objects.filter(**filter1).count()    
        
        
        
        returnValue = returnValue + "klm Id:" 
        
        #filter1 is updated here.    
        filter1['CompletionStatus'] = 'inprogress'  
        
        dima = None
        try:
            dima =  m.ql_masterattempts.objects.get(**filter1)
        except Exception as e:
            dima = None
            returnValue = returnValue + "innercatch" + str(e) 
            
        if dima is not None:            
            dima.Session_Id = sessionId
            dima.save()      
        else :             
            if diad.NumberOfAttempts == None or diad.NumberOfAttempts <= 0 or (diad.NumberOfAttempts > 0 and attemCount < diad.NumberOfAttempts) :
                ReportStatus = 'inactive'                                 
                dima = m.ql_masterattempts.objects.create(Assignment_Id = assignmentId,AssignmentTitle = assignmentTitle,Student_Id = studentId,
                Session_Id = sessionId,StudentName = studentName,Score = 0,Points = 0,Role = role,QL_Id = qlId,CompletionStatus ='inprogress',
                TimeSpent = 0,ReportStatus=ReportStatus,StartDate=datetime.now(),EndDate=datetime.now())
                
                if attemCount <= 0 :                    
                    filter231 = {"Assignment_Id": assignmentId, "AdditionalField1": qlId}
                    try:
                        qlassigadddeta = m.ql_assignmentadditionaldetails.objects.get(**filter231)
                        returnValue = returnValue + "NumOfUsers:" + str(qlassigadddeta.NumOfUsers)
                        qlassigadddeta.NumOfUsers = qlassigadddeta.NumOfUsers + 1
                        returnValue = returnValue + "after sum - NumOfUsers:" + str(qlassigadddeta.NumOfUsers)                    
                        qlassigadddeta.save()
                    except Exception as innr:
                        returnValue = returnValue + "NumOfUsers Update Error:" + str(innr)
                
        returnValue = returnValue + " - Launch Data Success"  
        
    except Exception as e :
            #DBLog("QL Interaction Error: Command=launch jsondata=" + "", e);
            returnValue = returnValue + "maincatch1" +  str(e) 
            
    return returnValue

def DBLog(msg, ex) :
    logstr = msg 
    if ex is not None :
        logstr = logstr + "==== ExceptionMessage:" + str(ex)+ ", ExceptionStacktrace:" 
               
    m.tbl_LogEntries.objects.create(LogDate = datetime.now(),LogString = logstr)

@csrf_exempt        
def QLSimTrendsAcrossQues(request):
    
    qlLst = GetSimList()
    
    #locLst = GetLocationList()          
    
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'ql_list': qlLst }
 
    return render_to_response('QLSimTrendsAcrossQues.html', context_dict, context_instance = context)

@csrf_exempt
def QLSimTrendsAcrossQuesDetails(request):
    selsim = request.GET.get('selsim', None)
    selloc = request.GET.get('selloc', None)
    
    qlQDRV = GetQuestionDetailsModel(selsim, selloc)
    
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('QLSimTrendsAcrossQuesDetails.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'QLReportView': qlQDRV }
 
    return render_to_response('QLSimTrendsAcrossQuesDetails.html', context_dict, context_instance = context)


#https://dev.econdip.pearsoncmg.com/econservice/knowdlanalytics/QLSimAnalytics/
@csrf_exempt
def QLSimAnalytics(request):
    QL_Id = request.GET.get('QL_Id', '')
    ASGN = request.GET.get('ASGN', '')
    qlLst = None
    asgnLst = None
           
    if QL_Id == "" and ASGN == "" :
        qlLst = GetSimList()
        asgnLst = GetAssignmentList()
    
    # Obtain the context from the HTTP request.
    
    context = RequestContext(request)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'ql_list': qlLst, 'asgn_list' : asgnLst }
  
    return render_to_response('QLSimAnalytics.html', context_dict, context_instance = context)

@csrf_exempt
def QLSimAnalyticsDetails(request):
    QL_Id = request.GET.get('QL_Id', None)
    #LOC = request.GET.get('LOC', None)
    ASGN = request.GET.get('ASGN', None)
        
    if QL_Id !="" and ASGN != "" :
        filter1 = {"Assignment_Id": ASGN,"QL_Id": QL_Id}
        AssignmentTitle = m.ql_assignmentdetails.objects.filter(**filter1).values("AssignmentTitle").distinct()            
    else :
        AssignmentTitle = ""
    
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'AssignmentTitle': AssignmentTitle }
  
    return render_to_response('QLSimAnalyticsDetails.html', context_dict, context_instance = context)


@csrf_exempt
def QLSimOverview(request):
    selsim = request.GET.get('QL_Id', None)
    #selloc = request.GET.get('LOC', None)
    ASGN = request.GET.get('ASGN', None)
    qlQDRV = GetQuestionDetailsModel(selsim, "", ASGN)
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('Overview.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'QLReportView': qlQDRV }
 
    return render_to_response('Overview.html', context_dict, context_instance = context)


@csrf_exempt
def QLSimClassReport(request):
    selsim = request.GET.get('QL_Id', None)
    selloc = request.GET.get('LOC', None)
    ASGN = request.GET.get('ASGN', None)
    qlQDRV = GetQuestionDetailsModel(selsim, selloc, ASGN, True)
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('ClassReport.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'QLReportView': qlQDRV }
 
    return render_to_response('ClassReport.html', context_dict, context_instance = context)


@csrf_exempt
def QLSimStudentReport(request):
    selsim = request.GET.get('QL_Id', None)
    #selloc = request.GET.get('LOC', None)
    ASGN = request.GET.get('ASGN', None)
    qlQDRV = GetStudentDetailModel(selsim, "", ASGN)
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('StudentReport.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'QLReportView': qlQDRV }
 
    return render_to_response('StudentReport.html', context_dict, context_instance = context)


@csrf_exempt
def QLSimOutcomes(request):  
    selsim = request.GET.get('QL_Id', None)
    #selloc = request.GET.get('LOC', None)
    ASGN = request.GET.get('ASGN', None)
    qlQDRV = GetOutcomesModel(selsim, "", ASGN)
    # Obtain the context from the HTTP request.
    context = RequestContext(request)
    
    if qlQDRV == "No data found" :
        return render_to_response('Outcomes.html', { "Status" : "No data found" }, context_instance = context)
    
    # Context is a normal Python dictionary whose keys can be accessed in the template index.html
    context_dict = {'Status' : 'Data found' , 'QLReportView': qlQDRV }
 
    return render_to_response('Outcomes.html', context_dict, context_instance = context)
   


def GetOutcomesModel(selsim, selloc, ASGN = "") :
    selsim = selsim.decode('unicode-escape')
    
    model = Classes.QLOutcomesModel()
    filterASGN = {"QL_Id": selsim}
    if ASGN :
        filterASGN["Assignment_Id"] = ASGN 
    assignment = m.ql_assignmentdetails.objects.filter(**filterASGN).values("ObjectiveDetails").all()    
    
    if assignment.count() == 0 :
        return model
    asgnob = assignment[0]
    jsonObjDetail = literal_eval(asgnob["ObjectiveDetails"])
    model.Description = str(jsonObjDetail["Title"])
    model.Title = str(jsonObjDetail["CustomTarget"])
    
    filterASGN['ReportStatus'] = 'active'
    mstattempts = m.ql_masterattempts.objects.filter(**filterASGN).all()
    
    #get total attempted count
    mstattempids = mstattempts.values_list("Id")
    model.TotalAttempted = mstattempts.values("Student_Id").distinct().count()
    j_objectives = jsonObjDetail["ObjectiveDetails"]
    model.ChartData = "["
    for obj in j_objectives :
        objective = Classes.QLOutcomeObjectiveModel()
        objective.Id = obj["Id"]
        objective.Name = obj["Name"]
        objective.Title = obj["Title"]
        objective.Questions = [] #new List<QLOutcomesQuestionModel>()
        j_pageids = obj["PageIds"]
        pageids = []
        for pg in j_pageids :
            question = Classes.QLOutcomesQuestionModel()
            question.QuestionId = pg
            filterQues = {"QL_Id": selsim ,  "QuestionId" : question.QuestionId }
            masterQ = m.ql_masterquestions.objects.filter(**filterQues).all()
            if masterQ is not None and masterQ.count() > 0 :
                mQues = masterQ[0]
                question.QuestionText = mQues.QuestionText
                question.QuestionTitle = mQues.QuestionTitle
                filterScr = {"QuestionId" : question.QuestionId, "MstAttemptId__in" : mstattempids }
                attscorequery = m.ql_questionattemptdetails.objects.filter(**filterScr)                            
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
        presscorelist = m.ql_questionattemptdetails.objects.filter(**filterScr1)
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
    
def GetStudentDetailModel(selsim, selloc, ASGN = "") :
    selsim = selsim.decode('unicode-escape')
    filter1 = {"QL_Id": selsim}
    lstQLMasterQ = m.ql_masterquestions.objects.filter(**filter1).all()
    
    filter2 = {"QL_Id": selsim, 'ReportStatus' : 'active'}
    qlMasterAttempts = None
    
    if ASGN :
        filter2["Assignment_Id"] = ASGN 
        qlMasterAttempts = m.ql_masterattempts.objects.filter(**filter2)
    else :
        qlMasterAttempts = m.ql_masterattempts.objects.filter(**filter2)
    
    if qlMasterAttempts.count() == 0 :
        return "No data found"
    
    lstQLMasterAttemptsId = qlMasterAttempts.values_list("Id")
    
    filter3 = {'MstAttemptId__in' :lstQLMasterAttemptsId }
    lstQLQuestionAttemptDetails = m.ql_questionattemptdetails.objects.filter(**filter3).all()
    
    qlSRV = Classes.QLStudentReportView()
    qlSRV.Results = []  # List<QLStudentDetails>()
    qlSRV.QuestionsDetails = [] # List<QlQuestionMasterForStudentReport>()
    
    for qlMa in qlMasterAttempts :
        student = Classes.QLStudentDetails()
        stuattempts = None
        student.Name = qlMa.StudentName 
        student.Id = qlMa.Student_Id 
        student.MasterAttemptId = qlMa.Id
        student.Score = 0.0 if qlMa.Score is None else qlMa.Score
        student.CompletionStatus = "Completed"  if qlMa.CompletionStatus == "complete" else "In Progress"
        
        stuattempts = None
        
        filterSAttmpt = {"QL_Id": selsim, 'CompletionStatus' : 'complete'}
        if ASGN :
            filterSAttmpt["Student_Id"] = qlMa.Student_Id
            filterSAttmpt["Assignment_Id"] = ASGN            
            stuattempts = m.ql_masterattempts.objects.filter(**filterSAttmpt).all()
        else :
            stuattempts = m.ql_masterattempts.objects.filter(**filterSAttmpt).all()
        
        student.Attempts = []  # List<QLStudentAttempt>()
        if stuattempts is not None and stuattempts.count() > 0 :
            k = 1 
            for std in stuattempts : 
                statt = Classes.QLStudentAttempt()
                statt.AttemptNo = k
                statt.Score =  0.00 if std.Score is None else std.Score
                statt.SessionId = std.Session_Id
                student.Attempts.append(statt)
                k = k + 1
        # end if stuattempts is not None and stuattempts.count() > 0 :
        
        student.Questions = []  # List<QLQuestionForStudentReport>()
        filterSQues = { "MstAttemptId" : qlMa.Id}
        studentQuestionsDetails = lstQLQuestionAttemptDetails.filter(**filterSQues).all()
        if studentQuestionsDetails and studentQuestionsDetails.count() > 0 :
            sameqs = []
            for qlqd in studentQuestionsDetails :
                filterQues = {  "QuestionId" : qlqd.QuestionId }
                quesMasterLst = lstQLMasterQ.filter(**filterQues).all()
                quesMaster = quesMasterLst[0]
                if ObjectExistInArray(qlSRV.QuestionsDetails,"Id", qlqd.QuestionId) is False:
                    question = Classes.QlQuestionMasterForStudentReport()
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
                        filtersmq = { 'QL_Id' : selsim, 'QuestionTitle' : question.QuestionTitle }
                        if m.ql_masterquestions.objects.filter(**filtersmq).count() > 1 :
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
                qlquestion = Classes.QLQuestionForStudentReport()
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
 
def GetQuestionDetailsModel(selsim, selloc, ASGN = "" , isStudentDetails = False) :
    #'unicode-escape' is used to escape sequences in string
    selsim = selsim.decode('unicode-escape')
    
    filter1 = {"QL_Id": selsim}
    lstQLMasterQ = m.ql_masterquestions.objects.filter(**filter1).all()
    packagerelPath = getOptionPath(selsim)    
    if (packagerelPath.find('/qualsims') != -1):
        packagerelPath = packagerelPath.replace('/qualsims', 'qualsims')        
        
    filter2 = {"QL_Id": selsim, 'ReportStatus' : 'active'}
    qlMasterAttempts = None
    
    if ASGN :
        filter2["Assignment_Id"] = ASGN 
        qlMasterAttempts = m.ql_masterattempts.objects.filter(**filter2)
    else :
        qlMasterAttempts = m.ql_masterattempts.objects.filter(**filter2)
    
    if qlMasterAttempts.count() == 0 :
        return " No data found"
     
    lstQLMasterAttemptsId = qlMasterAttempts.values_list("Id")
    
    filter3 = {'MstAttemptId__in' :lstQLMasterAttemptsId }
    lstQLQuestionAttemptDetails = m.ql_questionattemptdetails.objects.filter(**filter3).all()
    
    sameqs = []
    
    qlQDRV = Classes.QLQuestionDetailReportView()
    qlQDRV.Results = []
    
    for qlMqd in lstQLMasterQ :
        qlQDR = Classes.QLQuestionDetailReport()
        
        if qlMqd.QuestionText is not None :
            qlQDR.Text = qlMqd.QuestionText.encode("utf-8")
        
        qlQDR.Id = qlMqd.QuestionId
        qlQDR.OccurenceNo = ""
        
        if qlMqd.QuestionTitle is not None :
            qlQDR.QuestionTitle = qlMqd.QuestionTitle.encode("utf-8")
            # same question occurance no
            filtersmq = { 'QL_Id' : selsim, 'QuestionTitle' : qlQDR.QuestionTitle }
            if m.ql_masterquestions.objects.filter(**filtersmq).count() > 1 :
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
                student = Classes.QLStudentDetails()                
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
                qlOptionReport = Classes.QlOptionReport()
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

def GetSimList():
    # Retrieve a list of ql sim id distinct
    qlAssignment = m.ql_assignmentdetails.objects.all()
 
    qlLst = {}
    qlLst[""] = "Select Simulation"
    
    if qlAssignment.count() > 0 :
        for ql in qlAssignment :
            if qlLst.__contains__(ql.QL_Id) == False :
                title = ComnFunc.GetFormattedName(ql.QLTitle)
                qlLst[ql.QL_Id] = title
    return qlLst

def GetLocationList():
    locLst = {}
    
    lstDIAD = m.ql_assignmentdetails.objects.values('AssignmentLocation').distinct()
    
    if lstDIAD.count() > 0 :
        for loc in lstDIAD :
            if loc['AssignmentLocation'] != "" :
                loctxt = ""
                try :
                    str(loc['AssignmentLocation']).index("dev.econdip")
                    loctxt = ComnFunc.GetFormattedName("Spider")
                except ValueError : 
                    loctxt = ComnFunc.GetFormattedName("Prod")
                locLst[loc['AssignmentLocation']] = loctxt
    return locLst

def GetAssignmentList():
    # Retrieve a list of ql sim id distinct
    qlAssignment = m.ql_assignmentdetails.objects.all()
 
    asgnLst = {}
    asgnLst[""] = "Select Assignment"
    
    if qlAssignment.count() > 0 :
        for ql in qlAssignment :
            if asgnLst.__contains__(ql.Assignment_Id) == False :
                title = ComnFunc.GetFormattedName(ql.QLTitle)
                asgnLst[ql.Assignment_Id] = title
    return asgnLst

@csrf_exempt
def GetAssignmentsString(request):
    QL_Id = request.GET.get('QL_Id', None)
    optionString = "<option value=''>Select Assignment</option>"
    filter1 = {"QL_Id": QL_Id }
    qlAssignments = m.ql_assignmentdetails.objects.filter(**filter1).values("Assignment_Id","AssignmentTitle").order_by("AssignmentTitle").all()
        
    if qlAssignments.count() > 0 :    
        for asgmnt in qlAssignments :
            if optionString.find("value='" + asgmnt["Assignment_Id"] + "'") == -1 :
                optionString = optionString + "<option value='" + asgmnt["Assignment_Id"] + "'>" + asgmnt["AssignmentTitle"] + "</option>"

    return HttpResponse(optionString)


@csrf_exempt
def GetLocQLString(request):
    loc = request.GET.get('LOC', None)
    optionString = "<option value=''>Select Simulation</option>"
    filter1 = {"AssignmentLocation": loc}
    qlmediaarr = m.ql_assignmentdetails.objects.filter(**filter1).values("QL_Id","QLTitle").order_by("QLTitle").all()
    #print qlmediaarr.count() 
    if qlmediaarr.count() > 0 :
        for ql in qlmediaarr :
            if optionString.find("value='" + ql["QL_Id"] + "'") == -1 :
                optionString += "<option value='" + ql["QL_Id"] + "'>" + ql["QLTitle"] + "(" + ql["QL_Id"] + ")" + "</option>"

    return HttpResponse(optionString)

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
def fGetAddData(request) :    
    try:
        qlassigadddeta = m.ql_assignmentadditionaldetails.objects.all()
        resstr = str(len(qlassigadddeta))
        if len(qlassigadddeta) >0:    
            for qlassigadddetasingl in qlassigadddeta :
                resstr = resstr + "<br>QL Id=" + str(qlassigadddetasingl.AdditionalField1) + "Assign Id=" + str(qlassigadddetasingl.Assignment_Id) + "Total score=" + str(qlassigadddetasingl.TotalScore) + " Number of users=" + str(qlassigadddetasingl.NumOfUsers)
                
    except Exception as e:
        resstr = resstr + str(e)
        
    return HttpResponse(resstr)






        
        






#End of File




