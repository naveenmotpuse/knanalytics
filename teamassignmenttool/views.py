#System imports
from django.views.decorators.csrf import csrf_exempt 
from django.shortcuts import render      
from django.utils import timezone
from django.http import HttpResponse
import json

#Third-party imports

#Local source tree imports
from teamassignmenttool import models as mdl

#remaining-change this hard coded value later
gSttngMaxStudents = 5
gSttngTimeLimit = 10
gSttngTeamScore = 70
gSttngStudScore = 30
gSttngTimeLScl = "minutes"
gSttngPollRes = "submit"
 
def testcall(request):
    stdResponses = mdl.TMStudQuestionResponse.objects.raw("select -1 as Id, count(StudentId) as ModuleId,r.SelectedOption as SelectedOption from tmstudquestionsresponse r where r.IsQuestionAnswered = 1 group by r.TeamId, r.QuestionId, r.SelectedOption")
    #stdResponses = mdl.TMStudQuestionResponse().GetAll({ "TeamId" : 1, "QuestionId" : 1})
    #scnt = stdResponses.aggregate(Sum('SelectedOption'))
    result = list(stdResponses)
    for res in result :
        res.ModuleId
        res.SelectedOption
    return render(request, "Blank.html", {'data':  "msg"})

def showteamtable(request):
    try :
        stdEmail = request.GET.get('stdemail')
        moduleId = request.GET.get('moduleid')
        courseId = request.GET.get('courseid')
        assignmentId = request.GET.get('assignmentid')
        
        temp = stdEmail.split("@")
        jsondata= ""
        result = mdl.CommonSPData.objects.raw("call getwelcomepagedata(%s,%s,%s,%s,%s)",[stdEmail, temp[0], moduleId, assignmentId, courseId])
        result =list(result)
        if result.__len__() > 0 :
            jsondata = result[0].Column1
        
        #using SSE to send response 
        resp = HttpResponse()
        resp["Content-Type"] = "text/event-stream" #imp for SSE to work
        resp["Cache-Control"] = "no-cache"
        
        resp.write("data: " + jsondata +"\n\nretry:7000\n\n")
        
        return resp
    except Exception as ex :
        #AddErrorLogEntry(request.user.username,"showteamtable---"+str(ex))
        resp = HttpResponse()
        resp["Content-Type"] = "text/event-stream" #imp for SSE to work
        resp["Cache-Control"] = "no-cache"
        
        resp.write("data: " + "error#" + str(ex) +"\n\nretry:7000\n\n") #imp for SSE to work
        return resp
    
@csrf_exempt
def createorupdateteam(request):
    msg =""
    try :
        teamName = request.POST.get('teamname')
        teamId = int(request.POST.get('teamid','-1')) # check cond for teamId != -1 for further use if any
        courseId = request.POST.get('courseid')
        moduleId = request.POST.get('moduleid')
        assignmentId = request.POST.get('assignmentid')
        
        teamObj = mdl.TMTeams().GetObject({"Id" : teamId, "CourseId" : courseId })
        if teamObj :
            teamNameCnt = mdl.TMTeams().GetCount({"Name__icontains" : teamName.lower() , "CourseId" : courseId },{"Id" : teamId })
            if teamNameCnt == 0 :
                teamObj.Name = teamName 
                teamObj.save()
                msg = str(teamObj.Id)
            else :
                msg = "error#" + "Team name already exist. Please choose another."
        else :  
            teamNameCnt = mdl.TMTeams().GetCount({"Name__icontains" : teamName.lower() , "CourseId" : courseId })
            if teamNameCnt == 0 :
                teamObj = mdl.TMTeams().CreateObject({"Name" : teamName , "CourseId" : courseId })
                msg = str(teamObj.Id)
            else :
                msg = "error#" + "Team name already exist. Please choose another."
                
        if msg.find("error#") == -1 : 
            #check if team assignment details record exist if not then add new    
            teamAsgnObj = mdl.TMTeamAssignments().GetCount({"TeamId" : teamObj.Id, "ModuleId" : moduleId, "AssignmentId" : assignmentId})
            if teamAsgnObj == 0 :
                mdl.TMTeamAssignments().CreateObject({"TeamId" : teamObj.Id, "ModuleId" : moduleId, "AssignmentId" : assignmentId})
            
    except Exception as ex :
        #AddErrorLogEntry(request.user.username,"createorupdateteam---"+str(ex))
        msg = "error#" + str(ex)
            
    return render(request, "Blank.html", {'data':  msg})

@csrf_exempt
def addstudtoteam(request):
    msg ="success"
    try :
        teamId = int(request.POST.get('teamid'))
        studId = int(request.POST.get('studid'))
        courseId = request.POST.get('courseid')
        moduleId = request.POST.get('moduleid')
        assignmentId = request.POST.get('assignmentid')
        
        stdTeamOb = mdl.TMTeamDetails().GetObject({"StudentId" : studId, "CourseId" : courseId })
        if stdTeamOb : 
            stdTeamOb.TeamId = teamId 
            stdTeamOb.save()
        else :
            mdl.TMTeamDetails().CreateObject({"StudentId" : studId, "TeamId" : teamId, "CourseId" : courseId })
        
        #get max no of students per team allowed
        settDtls = mdl.TMSettingsDetails().GetObject({"ModuleId" : moduleId, "AssignmentId" : assignmentId }, ["Id","MaxStudents"])
        
        #check whether all teams full for that course
        teamGroup = mdl.TMTeamDetails.objects.raw("select t.Id, t.Name from tmteams t where t.CourseId = '{0}' and t.Id not in (select r.TeamId from tmteamdetails r \
            where r.CourseId = '{0}' group by r.TeamId having count(r.TeamId) = {1});".format(courseId, settDtls["MaxStudents"]))
        teamGroup = list(teamGroup)
        
        if teamGroup and teamGroup.__len__() > 0:
            #teams are not full yet
            pass
        else :
            #teams are full create new team
            temMaxId = mdl.TMTeams().GetMaxId()
            mdl.TMTeams().CreateObject({"Name" : "Team " + str(temMaxId +1), "CourseId" : courseId })
        
    except Exception as ex :
        #AddErrorLogEntry(request.user.username,"addstudtoteam---"+str(ex))
        msg = "error#" + str(ex)
            
    return render(request, "Blank.html", {'data':  msg})


def getstudteamdetails(request):
    msg =""
    try :
        courseId = request.GET.get('courseid')
        moduleId = request.GET.get('moduleid')
        assignmentId = request.GET.get('assignmentid')
        stdEmail = request.GET.get('stdemail')
        
        jsondata= ""
        result = mdl.CommonSPData.objects.raw("call getintroductionpagedata(%s,%s,%s,%s)",[stdEmail, moduleId, assignmentId, courseId])
        result =list(result)
        if result.__len__() > 0 :
            jsondata = result[0].Column1
        
        #using SSE to send response 
        resp = HttpResponse()
        resp["Content-Type"] = "text/event-stream" #imp for SSE to work
        resp["Cache-Control"] = "no-cache"
        
        resp.write("data: " + jsondata +"\n\nretry:7000\n\n")
        
        return resp
    except Exception as ex :
        #AddErrorLogEntry(request.user.username,"getstudteamdetails---"+str(ex))
        resp = HttpResponse()
        resp["Content-Type"] = "text/event-stream" #imp for SSE to work
        resp["Cache-Control"] = "no-cache"
        
        resp.write("data: " + "error#" + str(ex) +"\n\nretry:7000\n\n")
        return resp
    
@csrf_exempt
def addquestionresponse(request):
    moduleId = request.POST.get('moduleid')
    courseId = request.POST.get('courseid')
    assignmentId = request.POST.get('assignmentid')
    stdid = int(request.POST.get('stdid'))
    questionid = int(request.POST.get('questionid'))
    teamid = int(request.POST.get('teamid'))
    selOption = request.POST.get('seloption')
    isCorrect = int(request.POST.get('iscorrect'))
    IsQuestionAnswered = int(request.POST.get('isquestionanswered'))
    gLastQuestionId = int(request.POST.get('glastquestionid'))
    gTotalQCnt  = int(request.POST.get('gtotalqcnt'))
    
    msg = "success"
    try :
        qresMdl = mdl.TMStudQuestionResponse()
        qresMdl.CreateObject({"IsQuestionAnswered" : IsQuestionAnswered, "ModuleId" : moduleId, "TeamId" :teamid, "StudentId" :stdid, "QuestionId": questionid, 
            "SelectedOption" : selOption,"IsCorrect" : isCorrect,  "ModuleId" : moduleId, "AssignmentId" : assignmentId })
    
        totStudCnt = mdl.TMTeamDetails().GetCount({"TeamId" : teamid, "CourseId" : courseId})
        stdAnswrdCnt = qresMdl.GetCount({ "TeamId" : teamid , "QuestionId" : questionid , "ModuleId" : moduleId, "AssignmentId" : assignmentId })
        teamAsgnObj = mdl.TMTeamAssignments().GetObject({"TeamId" : teamid, "ModuleId" : moduleId, "AssignmentId" : assignmentId })
        if stdAnswrdCnt == 1 :
            teamAsgnObj.IsTimerStarted = 1
            teamAsgnObj.TimerDate = timezone.now()
            teamAsgnObj.QuestionId = questionid
            teamAsgnObj.save()
        elif stdAnswrdCnt == totStudCnt :
            teamAsgnObj.IsTimerStarted = 0
            teamAsgnObj.TimerDate = None
            teamAsgnObj.QuestionId = -1
            teamAsgnObj.save()
            if questionid == gLastQuestionId :
                msg = calculateteamscore(request.user.username,moduleId, teamid, assignmentId, stdid,gTotalQCnt)
        return render(request, "Blank.html", {'data':  msg})
    except Exception as ex :
        
        msg = 'error#There was an error adding question response.for moduleid={0},stdid={1},questionid={2},teamid={3}, selOption={4},IsQuestionAnswered={5}, courseId={6},assignmentId={7}'.format(moduleId,stdid,questionid,teamid,selOption,IsQuestionAnswered,courseId,assignmentId)
        msg += str(ex)
        #AddErrorLogEntry(request.user.username,msg)
        return render(request, "Blank.html", {'data':  msg})

def checkquestionstatus(request):
    try :
        stdEmail = request.GET.get('stdemail')
        questionid = int(request.GET.get('questionid'))
        moduleId = request.GET.get('moduleid')
        courseId = request.GET.get('courseid')
        assignmentId = request.GET.get('assignmentid')
        gLastQuestionId = int(request.GET.get('glastquestionid'))

        jsondata= ""
        result = mdl.CommonSPData.objects.raw("call getquestionpagedata(%s,%s,%s,%s,%s,%s)",[stdEmail, moduleId, assignmentId, courseId,questionid,gLastQuestionId])
        result =list(result)
        if result.__len__() > 0 :
            jsondata = result[0].Column1
            jsonCol2 = result[0].Column2
            if jsonCol2 and jsonCol2 != '' :
                msg = json.loads(jsonCol2)
                if "CalculateScore" in msg and msg["CalculateScore"] == 1:
                    tData = json.loads(jsondata)
                    msg = calculateteamscore(request.user.username, moduleId, tData["TeamId"], assignmentId, tData["StudId"])
                    jsondata = jsondata + "###" + msg
                else :
                    jsondata = jsondata + "###" + jsonCol2
        
        #using SSE to send response 
        resp = HttpResponse()
        resp["Content-Type"] = "text/event-stream" #imp for SSE to work
        resp["Cache-Control"] = "no-cache"
        
        resp.write("data: " + jsondata +"\n\nretry:7000\n\n")
        
        return resp
    except Exception as ex :
        #AddErrorLogEntry(request.user.username,"checkquestionstatus---"+str(ex))
        resp = HttpResponse()
        resp["Content-Type"] = "text/event-stream" #imp for SSE to work
        resp["Cache-Control"] = "no-cache"
        
        resp.write("data: " + "error#" +str(ex) +"\n\nretry:7000\n\n")
        return resp

@csrf_exempt
def donotdisplaymsgagain(request):
    msg = "success"
    try :            
        studId = int(request.POST.get('studid'))
        moduleId = request.POST.get('moduleid')
        assignmentId = request.POST.get('assignmentid')
        
        tmstdObj = mdl.TMStudentScore().GetObject({"ModuleId" : moduleId, "AssignmentId" : assignmentId, "StudentId" :studId})
        if not tmstdObj : 
            mdl.TMStudentScore().CreateObject({"ModuleId" : moduleId, "AssignmentId" : assignmentId, "StudentId" :studId, "DoNotShowMsgAgain" : 1})
            
    except Exception as ex :
        msg = "error#donotdisplaymsgagain--"+str(ex)
        #AddErrorLogEntry(request.user.username,msg)
    return render(request, "Blank.html", {'data':  msg})

def getdonotdisplaymsgvalue(request):
    msg = 0
    try :            
        studId = int(request.GET.get('studid'))
        moduleId = request.GET.get('moduleid')
        assignmentId = request.GET.get('assignmentid')
        
        tmstdObj = mdl.TMStudentScore().GetObject({"ModuleId" : moduleId, "AssignmentId" : assignmentId, "StudentId" :studId},["Id","DoNotShowMsgAgain"])
        if tmstdObj : 
            msg = tmstdObj["DoNotShowMsgAgain"]
            
    except Exception as ex :
        msg = "error#getdonotdisplaymsgvalue--"+str(ex)
        #AddErrorLogEntry(request.user.username,msg)
    return render(request, "Blank.html", {'data':  msg})

def calculateteamscore(loggedInUser, moduleId, teamId, assignmentId, studId, gTotalQCnt):
    msg = ""
    try :
        result = mdl.CommonSPData.objects.raw("call getteamstdscore(%s,%s,%s,%s,%s)",[teamId, gTotalQCnt, moduleId, assignmentId, studId])
        result =list(result)
        if result.__len__() > 0 :
            temp = result[0].Column1
            if temp and temp != '':
                msg = temp
        
    except Exception as ex :
        msg = "error#calculatescore--"+str(ex)
        #AddErrorLogEntry(loggedInUser,msg)
        
    return msg

def getteamscore(loggedInUser,moduleId, teamId, assignmentId, studId) :
    msg = ""
    try :
        teamScore = mdl.TMTeamAssignments().GetObject({"TeamId" : teamId, "ModuleId" : moduleId, "AssignmentId" : assignmentId}, ["Id","TeamScore"])
        studScore = mdl.TMStudentScore().GetObject({"StudentId" : studId, "ModuleId" : moduleId, "AssignmentId" : assignmentId}, ["Id","Score"])
        
        if studScore :
            studScore =round(studScore["Score"])
            
        msg = '{"TeamScore":' + str(round(teamScore["TeamScore"])) + ',"CurrentStudent" : {"StudentId" :' + str(studId) + ',"Score":'+ str(studScore) + '}}'
    except Exception as ex :
        msg = "error#getteamscore--"+str(ex)
        #AddErrorLogEntry(loggedInUser,msg)
        
    return msg


