



import uuid
import json
from django.db import models
import datetime
from _mysql import NULL
from datetime import date

class RevelSettings(models.Model):
    API_KEY = "42a47ae3a36ad6a1a8b577848058e578"
    CLIENT_ID = "fI4Zr0fVKM7uU6uEueywORt1kfkkFpPU" 

class RevelAssignments(models.Model):
    assignmentId = models.CharField(max_length=120,null=False, db_index=True)
    assignmentType = models.CharField(max_length=120)
    title = models.TextField(default='')
    description = models.TextField(default='')
    templateId = models.CharField(max_length=120, db_index=True)
    courseId = models.CharField(max_length=120, db_index=True)
    dueTime = models.DateTimeField(default=None, null=True)
    dueTimeUTCMilliseconds = models.CharField(max_length=20,null=True)
    metadata = models.TextField(default='{}') 
    sourceCourseId = models.CharField(max_length=120)
    sourceAssignmentId = models.CharField(max_length=120)    
    
    @classmethod
    def CreateAssignment(cls, jsonData, userId):        
        assign_title = ''
        assign_desc = ''
        assign_dueTime = datetime.datetime.now() + datetime.timedelta(days=100*365)
        assign_dueTimeMill =  assign_dueTime.microsecond/1000 + assign_dueTime.second*1000 
        assign_metadata = '{}'
        duedateflag = ""
        
        if jsonData.get('title'):
            assign_title = jsonData['title']
	    assign_title = assign_title.encode("ascii","ignore")
            #assign_title = u''.join(jsonData['title']).encode('utf-8').strip()

        if jsonData.get('description'):
            assign_desc = jsonData['description']
        if jsonData.get('dueTime'):
            try:
                assign_dueTimeMill = jsonData['dueTime']            
                assign_dueTime = datetime.datetime.fromtimestamp(assign_dueTimeMill / 1000)
            except Exception as dtexe:
                duedateflag = "NoDueDate"
        else:
            duedateflag = "NoDueDate"
                
        if jsonData.get('metadata'):
            assign_metadata = json.dumps(jsonData['metadata'])            
                
        r_assignment = cls.objects.create(
            assignmentId = str(uuid.uuid4()), 
            assignmentType = jsonData['assignmentType'], 
            title = assign_title,                                         
            description = assign_desc, 
            templateId = jsonData['templateId'],
            courseId = jsonData['courseId'],
            dueTime = assign_dueTime,
            dueTimeUTCMilliseconds = assign_dueTimeMill,
            metadata = assign_metadata
            #,
            #createDate = timezone.now(),
            #createBy =  userId,
            #updateDate =  timezone.now(),
            #updateBy = userId                                    
        )
        r_assignment.save() 
        traceval = ""
        try:        
            setdata = '{"AllowedAttempts":0, "ShowClassAvg":true, "TargetPoints":1, "AllowSubmission": true}'            
            RevelAssignmentDetails.objects.create(assignmentId=r_assignment.assignmentId,
                                                            courseId=r_assignment.courseId, templateId=r_assignment.templateId, 
                                                            settingsData=setdata, lastUpdateFor = "Create default assignment details", additionalField3=duedateflag, objectiveDetails="{}")
        except Exception as innrex:
            jsonData['Trace'] = str(innrex)
            
               
        jsonData['duedateflag'] = duedateflag
        if jsonData.get('activities'):
            for actvityjson in jsonData['activities']:
                RevelActivities.AddUpdateActivity(r_assignment.courseId, r_assignment.assignmentId, actvityjson)                
        
        jsonData['assignmentId'] = r_assignment.assignmentId              
        return jsonData    
    
    @classmethod
    def CopyAssignment(cls, jsonData, userId):        
        assign_title = ''
        assign_desc = ''
        assign_dueTime = NULL
        assign_dueTimeMill = NULL
        assign_metadata = '{}'
        assign_srcCourseId = ''
        assign_srcAssignId = ''
        
        if jsonData.get('title'):
            assign_title = jsonData['title']
        if jsonData.get('description'):
            assign_desc = jsonData['description']
        if jsonData.get('dueTime'):
            assign_dueTimeMill = jsonData['dueTime']            
            assign_dueTime = datetime.datetime.fromtimestamp(assign_dueTimeMill / 1000)
        if jsonData.get('metadata'):
            assign_metadata = json.dumps(jsonData['metadata'])     
        if jsonData.get('sourceCourseId'):
            assign_srcCourseId = jsonData['sourceCourseId']
        if jsonData.get('sourceAssignmentId'):
            assign_srcAssignId = jsonData['sourceAssignmentId']           
                
        r_assignment = cls.objects.create(
            assignmentId = str(uuid.uuid4()), 
            assignmentType = jsonData['assignmentType'], 
            title = assign_title,                                         
            description = assign_desc, 
            templateId = jsonData['templateId'],
            courseId = jsonData['courseId'],
            dueTime = assign_dueTime,
            dueTimeUTCMilliseconds = assign_dueTimeMill,
            metadata = assign_metadata,
            sourceCourseId = assign_srcCourseId,
            sourceAssignmentId = assign_srcAssignId                                               
        )
        r_assignment.save()  
        
        if jsonData.get('activities'):
            for actvityjson in jsonData['activities']:
                RevelActivities.AddUpdateActivity(r_assignment.courseId, r_assignment.assignmentId, actvityjson)                
        
        #Anu 11-nov-2017 copy assignment settings from source assignment        
        settingsList = RevelAssignmentDetails.objects.filter(assignmentId=assign_srcAssignId, courseId=assign_srcCourseId).values("templateId","settingsData").all()
        if settingsList.count > 0 :
            for r_setting in settingsList :                
                tempJsn = r_setting["settingsData"]
                tempTId = r_setting["templateId"]
                r_settingNew = RevelAssignmentDetails.objects.create(assignmentId = r_assignment.assignmentId, templateId = tempTId, courseId = r_assignment.courseId, settingsData = tempJsn)
                r_settingNew.save()

        retObj ={}
        retObj['assignmentId'] = r_assignment.assignmentId 
        retObj['assignmentType'] = r_assignment.assignmentType
        retObj['title'] = r_assignment.title                                         
        retObj['description'] = r_assignment.description 
        retObj['templateId'] = r_assignment.templateId
        retObj['courseId'] = r_assignment.courseId
        retObj['dueTime'] = r_assignment.dueTimeUTCMilliseconds            
        retObj['metadata'] = jsonData['metadata']        
        retObj['activities'] = jsonData['activities']  
                  
        return retObj

    @classmethod
    def UpdateAssignment(cls, jsonData, userId): 
        assign_Id = ''   
        assign_title = ''
        assign_desc = ''
        assign_dueTime = NULL
        assign_dueTimeMill = NULL
        assign_metadata = '{}'
        
        if jsonData.get('assignmentId'):
            assign_Id = jsonData['assignmentId']
            if jsonData.get('title'):
                assign_title = jsonData['title']
            if jsonData.get('description'):
                assign_desc = jsonData['description']
            if jsonData.get('dueTime'):
                assign_dueTimeMill = jsonData['dueTime']            
                assign_dueTime = datetime.datetime.fromtimestamp(assign_dueTimeMill / 1000)
            if jsonData.get('metadata'):
                assign_metadata = json.dumps(jsonData['metadata'])           
                    
            r_assignments = cls.objects.filter(assignmentId=assign_Id)        
            if(r_assignments.count()>0): 
                r_assignment = r_assignments[0]  
                if assign_title != '':
                    r_assignment.title = assign_title                
                if assign_desc != '':
                    r_assignment.description = assign_desc
                if assign_dueTimeMill != NULL:
                    r_assignment.dueTimeUTCMilliseconds = assign_dueTimeMill
                    r_assignment.dueTime = assign_dueTime
                if assign_metadata != '{}':
                    r_assignment.metadata = assign_metadata
                
                
                #r_assignment.updateDate =  timezone.now(),
                #r_assignment.updateBy = userId 
                
                r_assignment.save()
                
                r_assignmentdetls = RevelAssignmentDetails.objects.filter(assignmentId=r_assignment.assignmentId)
                if(r_assignmentdetls.count()>0): 
                    r_assignmentdet = r_assignmentdetls[0] 
                    r_assignmentdet.additionalField3 = ""
                    r_assignmentdet.save()
                #update activity data.    
                if jsonData.get('activities'):
                    for actvityjson in jsonData['activities']:
                        RevelActivities.AddUpdateActivity(r_assignment.courseId, r_assignment.assignmentId, actvityjson)                  
            else:
                r_assignment = cls.objects.create(
                    assignmentId = assign_Id, 
                    assignmentType = jsonData['assignmentType'], 
                    title = assign_title,                                         
                    description = assign_desc, 
                    templateId = jsonData['templateId'],
                    courseId = jsonData['courseId'],
                    dueTime = assign_dueTime,
                    dueTimeUTCMilliseconds = assign_dueTimeMill,
                    metadata = assign_metadata 
                    #,
                    #createDate = timezone.now(),
                    #createBy =  userId,
                    #updateDate =  timezone.now(),
                    #updateBy = userId                                      
                )
                r_assignment.save()                
                #update activity data.          
                if jsonData.get('activities'):
                    for actvityjson in jsonData['activities']:
                        RevelActivities.AddUpdateActivity(r_assignment.courseId, r_assignment.assignmentId, actvityjson)

    @classmethod
    def DeleteAssignment(cls,course_id,assignment_id):
        RevelActivities.objects.filter(courseId = course_id, assignmentId = assignment_id).delete()
        cls.objects.filter(courseId = course_id, assignmentId = assignment_id).delete()
    
    @classmethod
    def DeleteAllAssignment(cls,course_id):
        if course_id == 'kall':            
            RevelActivities.objects.all().delete()
            cls.objects.all().delete()
        else:
            RevelActivities.objects.filter(courseId = course_id).delete()
            cls.objects.filter(courseId = course_id).delete()                
    
    @classmethod
    def GetAssignment(cls,course_id,assignment_id):
        retObj = {}
        assignments = cls.objects.filter(courseId = course_id, assignmentId = assignment_id)
        if assignments.count()>0:
            assignment = assignments[0]
            retObj['assignmentId'] = assignment.assignmentId 
            retObj['assignmentType'] = assignment.assignmentType
            retObj['title'] = assignment.title                                         
            retObj['description'] = assignment.description 
            retObj['templateId'] = assignment.templateId
            retObj['courseId'] = assignment.courseId
            retObj['dueTime'] = assignment.dueTimeUTCMilliseconds            
            retObj['metadata'] = json.loads(assignment.metadata)
            retObj['activities'] = []            
            #Get activity data.            
            activities = RevelActivities.objects.filter(courseId = course_id, assignmentId = assignment_id)  
            for activity in activities:
                acti = {}
                acti["activityId"] = activity.activityId 
                acti["activityType"] = activity.activityType
                acti["subType"] = activity.subType
                acti["seq"] = activity.seq
                acti["title"]  = activity.title                                        
                acti["description"] = activity.description
                acti["gradable"] = activity.gradable                      
                acti["metadata"] = activity.metadata 
                #acti["assignmentId"]  = activity.assignmentId               
                #acti["courseId"] = activity.courseId  
                retObj['activities'].append(acti)         
                                    
        else:
            retObj['assignmentId'] = assignment_id
            
        return retObj
    
    @classmethod
    def GetAllAssignment(cls,course_id):
        assignments = cls.objects.filter(courseId = course_id)
        if course_id == 'kall':
            assignments = cls.objects.all()
        
        dictList = []
        for asgn in assignments:
            retObj = {}
            retObj['assignmentId'] = asgn.assignmentId 
            retObj['assignmentType'] = asgn.assignmentType
            retObj['title'] = asgn.title                                         
            retObj['description'] = asgn.description 
            retObj['templateId'] = asgn.templateId
            retObj['courseId'] = asgn.courseId
            retObj['dueTime'] = asgn.dueTimeUTCMilliseconds            
            #retObj['metadata'] = json.loads(asgn.metadata)
            
            dictList.append(retObj)
            
        return dictList
    
    @classmethod
    def SaveReqMetaData(cls,param_dict, param_type):
        r_assignments = cls.objects.filter(assignmentId="knowdl_assignmentId", courseId="knowdl_courseId", assignmentType = param_type)           
        if(r_assignments.count()>0):
            r_assignment = r_assignments[0]
            r_assignment.description = str(param_dict)
            r_assignment.assignmentType = param_type,
            r_assignment.save()
        else:
            r_assignment = cls.objects.create(
                assignmentId = "knowdl_assignmentId", 
                assignmentType = param_type,
                title = "RequestHeader",
                description = str(param_dict),
                templateId = "knowdl_templateId",
                courseId = "knowdl_courseId",
                dueTime = datetime.datetime.fromtimestamp(1503916499614 / 1000),
                dueTimeUTCMilliseconds = "1503916499614",
                metadata = "{}"
            )
            r_assignment.save()    
    
    @classmethod
    def GetReqMetaData(cls):
        assignments = cls.objects.filter(assignmentId="knowdl_assignmentId", courseId="knowdl_courseId")
        dictList = []
        for asgn in assignments:
            retObj = {}
            retObj['assignmentId'] = asgn.assignmentId 
            retObj['assignmentType'] = asgn.assignmentType
            retObj['title'] = asgn.title                                         
            retObj['description'] = asgn.description 
            retObj['templateId'] = asgn.templateId
            retObj['courseId'] = asgn.courseId
            retObj['dueTime'] = asgn.dueTimeUTCMilliseconds            
            #retObj['metadata'] = json.loads(asgn.metadata)
            
            dictList.append(retObj)
            
        return dictList

class RevelActivities(models.Model):
    activityId = models.CharField(max_length=120,null=False, db_index=True)
    activityType = models.CharField(max_length=120)
    subType = models.CharField(max_length=120)
    seq = models.IntegerField(default=-1)
    title = models.CharField(max_length=200)    
    description = models.TextField(default='')
    gradable = models.BooleanField(default=False)
    metadata = models.TextField(default='{}')  
    assignmentId = models.CharField(max_length=120,null=False, db_index=True)
    courseId = models.CharField(max_length=120, db_index=True)

    @classmethod
    def AddUpdateActivity(cls,crseId, assignId, jsonData):        
        actv_title = ''
        actv_desc = ''       
        actv_metadata = '{}'
        actv_subType = ''
        actv_seq = -1
        actv_gradable = False
        actv_id = str(uuid.uuid4())
        
        if jsonData.get('activityId'):
            actv_id = jsonData['activityId']
        if jsonData.get('title'):
            actv_title = jsonData['title']
        if jsonData.get('description'):
            actv_desc = jsonData['description'] 
        if jsonData.get('subType'):
            actv_subType = jsonData['subType'] 
        if jsonData.get('seq'):
            actv_seq = int(jsonData['seq']) 
        if jsonData.get('gradable'):
            actv_gradable = bool(jsonData['gradable']) 
        if jsonData.get('metadata'):
            actv_metadata = json.dumps(jsonData['metadata'])    
            
        r_activities = cls.objects.filter(activityId=actv_id, courseId = crseId, assignmentId = assignId)              
        if(r_activities.count()>0): 
            r_activity = r_activities[0]
            r_activity.activityType = jsonData['activityType']
            if actv_subType != '':
                r_activity.subType = actv_subType
            r_activity.seq = actv_seq
            if actv_title != '':
                r_activity.title = actv_title   
            if actv_desc != '':                                  
                r_activity.description = actv_desc 
            r_activity.gradable = actv_gradable 
            if actv_metadata != '{}':                      
                r_activity.metadata = actv_metadata
                
            r_activity.save()            
        else:                
            r_activity = cls.objects.create(
                activityId = actv_id, 
                activityType = jsonData['activityType'],
                subType = actv_subType,
                seq = actv_seq,
                title = actv_title,                                         
                description = actv_desc, 
                gradable = actv_gradable,                        
                metadata = actv_metadata ,
                assignmentId = assignId,                
                courseId = crseId                       
            )
            r_activity.save()
    
class RevelAssignmentDetails(models.Model):
    assignmentId = models.CharField(max_length=120,null=False, db_index=True)
    templateId = models.CharField(max_length=120, db_index=True)
    courseId = models.CharField(max_length=120, db_index=True)    
    totalScore = models.DecimalField(default=0, max_digits=10, decimal_places=2) 
    numOfUsers = models.IntegerField(default=0)  
    settingsData = models.TextField(max_length=None)      
    objectiveDetails = models.TextField(max_length=None, null=True,default=None)     
    status = models.BooleanField(default=True) 
    createDate = models.DateTimeField(auto_now_add=True, editable=True)
    lastUpdateDate = models.DateTimeField(auto_now_add=True, editable=True)
    lastUpdateFor =  models.CharField(max_length=200, default="", null=True)
    additionalField1 = models.TextField(default="",null=True)
    additionalField2 = models.TextField(default="",null=True)
    additionalField3 = models.TextField(default="",null=True)
    
    @classmethod
    def get(cls, cId, aId, tId):
        asgnDetails = None
        try:
            asgnDetails = cls.objects.get(assignmentId=aId, courseId=cId, templateId=tId)            
        except Exception as ex: 
            setdata = '{"AllowedAttempts":0, "ShowClassAvg":true, "TargetPoints":1, "AllowSubmission": true}'             
            asgnDetails = cls.objects.create(assignmentId=aId, courseId=cId, templateId=tId, settingsData=setdata)  
            
        return asgnDetails 
    
    @classmethod
    def saveSettings(cls, cId, aId, tId, settingsData):
        #get or create session object.
        asgnDetails = None
        try:
            asgnDetails = cls.objects.get(assignmentId=aId, courseId=cId, templateId=tId)
            asgnDetails.settingsData = str(settingsData)
            asgnDetails.lastUpdateDate = datetime.datetime.now()
            asgnDetails.lastUpdateFor = "Updated Settings."
            asgnDetails.save()
        except Exception as ex:           
            asgnDetails = cls.objects.create(assignmentId=aId, courseId=cId, templateId=tId, settingsData = str(settingsData), lastUpdateFor="Save Settings") 
           
    
    @classmethod
    def getSettings(cls, cId, aId, tId):
        #get or create session object.
        asgnDetails = None
        try:
            asgnDetails = cls.objects.get(assignmentId=aId, courseId=cId, templateId=tId)            
        except Exception as ex:            
            asgnDetails = None
            
        return asgnDetails
    
class RevelMasterAttemptData(models.Model):    
    Id = models.AutoField(primary_key=True) 
    assignmentId = models.CharField(max_length=120,null=False, db_index=True)
    templateId = models.CharField(max_length=120, db_index=True)
    courseId = models.CharField(max_length=120, db_index=True)    
    Student_Id = models.CharField(max_length=120, db_index=True)     
    StudentName = models.CharField(max_length=200,default="",null=True)     
    Role = models.CharField(max_length=120,default=None,null=True) 
    StartDate = models.DateTimeField(auto_now_add=True, editable=True)
    EndDate = models.DateTimeField(auto_now_add=True, editable=True)
    CompletionStatus = models.CharField(max_length=120,default="inprogress") 
    TimeSpent =models.DecimalField(max_digits=10, decimal_places=2,default=0)
    Score = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    Points = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    ReportStatus = models.CharField(max_length=120,default="inactive") 
    stateData = models.TextField(default="{}")
    #additionalField1 is used to save request no.
    additionalField1 = models.TextField(default="",null=True)
    additionalField2 = models.TextField(default="",null=True)
    additionalField3 = models.TextField(default="",null=True) 
    
        
    @classmethod
    def create(cls, cId, aId, tId, sId, jsondatavalues):
        #get or create session object.        
        studentName = ""
        role = ""        
        atmpt = None                   
        if "StudentName" in jsondatavalues :
            studentName = jsondatavalues["StudentName"]    
        if "Role" in jsondatavalues :
            role = jsondatavalues["Role"]  
               
        atmpt = cls.objects.create(assignmentId=aId, courseId=cId, templateId=tId,Student_Id = sId,
                                   StudentName = studentName, Role = role, TimeSpent = 0, Score =0, Points = 0,
                                   CompletionStatus = 'inprogress')                  
            
        return atmpt 
    
    @classmethod
    def getLast(cls, cId, aId, tId, sId):   
        atmpt = cls.objects.filter(assignmentId=aId, courseId=cId, templateId=tId, Student_Id = sId).order_by("-StartDate").all()[0]
        return atmpt
    
class RevelQuestionAttemptDetails(models.Model):    
    Id = models.AutoField(primary_key=True) 
    MstAttemptId = models.IntegerField() 
    PageId = models.CharField(max_length=10,default="",null=True) 
    QuestionId = models.CharField(max_length=10,default="",null=True) 
    SelOptionId =  models.CharField(max_length=100,default="",null=True)
    CorrectStatus = models.CharField(max_length=50,default="",null=True)     
    Score = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    Points = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    TimeSpent = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    AdditionalInfo = models.TextField(default="",null=True)     
        
class RevelMasterQuestions(models.Model) :
    Id = models.AutoField(primary_key=True)    
    templateId = models.CharField(max_length=120, db_index=True)
    courseId = models.CharField(max_length=120, db_index=True)  
    PageId = models.CharField(max_length=50) 
    QuestionId = models.CharField(max_length=100) 
    QuestionText = models.TextField()
    Options = models.TextField()
    TotalPoints = models.DecimalField(max_digits=10, decimal_places=2) 
    QuestionTitle = models.CharField(max_length=1000)
    AdditionalInfo = models.CharField(max_length=500) 
    Type = models.CharField(max_length=50)    
    

    

    

# Create your models here.






