from django.db import models as m
from django.db.models import Max

# Create your models here.
class TMStudentDetails(m.Model) :
    Id = m.BigAutoField(primary_key=True)
    FirstName = m.CharField(max_length=250,null=False)
    LastName = m.CharField(max_length=250,null=False)
    Email = m.CharField(max_length=500,null=False)
    Status  = m.CharField(max_length=50,null=False)

    class Meta :
        db_table ='tmstudentdetails'
    
    def CreateObject(self,valObj):
        res = self.__class__.objects.create(FirstName = valObj["FirstName"],
                                            LastName = valObj["LastName"],
                                            Email = valObj["Email"],
                                            Status = valObj["Status"],)
        return res
    
    def GetIdList(self,filterVal):
        lst = self.__class__.objects.filter(**filterVal).values_list("Id", flat=True).all()
        return lst
    
    def GetObject(self,filterVal,fieldsLst=None):
        cnt = self.__class__.objects.filter(**filterVal).count()
        obj = None
        if cnt > 0 :
            if fieldsLst :
                obj = self.__class__.objects.filter(**filterVal).values(*fieldsLst).get()
            else :
                obj = self.__class__.objects.filter(**filterVal).get()        
        return obj
    
    def GetAll(self, filterVal, fieldsLst = None, isFltrQLst = False, orderby =None, startIndx = None,pageSize = None) :
        queryOb = None
        lst = None
        
        if isFltrQLst :
            queryOb =self.__class__.objects.filter(filterVal)
        else :
            queryOb =self.__class__.objects.filter(**filterVal)
        
        if fieldsLst :
            queryOb  = queryOb.values(*fieldsLst)
        
        if orderby :
            queryOb = queryOb.order_by(orderby)
        
        if pageSize :
            lst = queryOb.all()[startIndx:pageSize]
        else:
            lst = queryOb.all()
        
        return lst

class TMTeams(m.Model):
    Id = m.BigAutoField(primary_key=True)
    Name = m.CharField(max_length=500,null=False)
    CourseId = m.CharField(max_length=500,null=False)
    
    class Meta :
        db_table ='tmteams'
    
    def GetCount(self,filterVal,excludeVal=None):
        cnt = 0
        if excludeVal : 
            cnt = self.__class__.objects.filter(**filterVal).exclude(**excludeVal).count()
        else :
            cnt = self.__class__.objects.filter(**filterVal).count()
        return cnt

    def CreateObject(self,valObj):
        res = self.__class__.objects.create(Name = valObj["Name"],
                                            CourseId = valObj["CourseId"])
        return res
    
    def GetMaxId(self):
        res = self.__class__.objects.aggregate(Max("Id"))
        rmCnt = 0
        if res and len(res) > 0:
            if res['Id__max'] :
                rmCnt = res['Id__max']
        
        return rmCnt
        
    def UpdateObject(self,filterVal,updateVal):    
        cnt = self.__class__.objects.filter(**filterVal).count()
        if cnt > 0 :
            usr = self.__class__.objects.filter(**filterVal).update(**updateVal)
            return usr
    
    def GetObject(self,filterVal,fieldsLst=None):
        cnt = self.__class__.objects.filter(**filterVal).count()
        obj = None
        if cnt > 0 :
            if fieldsLst :
                obj = self.__class__.objects.filter(**filterVal).values(*fieldsLst).get()
            else :
                obj = self.__class__.objects.filter(**filterVal).get()        
        return obj
    
    def GetAll(self, filterVal, fieldsLst = None, isFltrQLst = False, orderby =None, startIndx = None,pageSize = None) :
        queryOb = None
        lst = None
        
        if isFltrQLst :
            queryOb =self.__class__.objects.filter(filterVal)
        else :
            queryOb =self.__class__.objects.filter(**filterVal)
        
        if fieldsLst :
            queryOb  = queryOb.values(*fieldsLst)
        
        if orderby :
            queryOb = queryOb.order_by(orderby)
        
        if pageSize :
            lst = queryOb.all()[startIndx:pageSize]
        else:
            lst = queryOb.all()
        
        return lst

class TMTeamDetails(m.Model) :
    Id = m.BigAutoField(primary_key=True)
    TeamId = m.BigIntegerField(null=False)
    StudentId = m.BigIntegerField(null=False)
    CourseId = m.CharField(max_length=500,null=False)

    class Meta :
        db_table ='tmteamdetails'
    
    def CreateObject(self,valObj):
        res = self.__class__.objects.create(TeamId = valObj["TeamId"],
                                            StudentId = valObj["StudentId"],
                                            CourseId = valObj["CourseId"])
        return res

    def GetObject(self,filterVal,fieldsLst=None):
        cnt = self.__class__.objects.filter(**filterVal).count()
        obj = None
        if cnt > 0 :
            if fieldsLst :
                obj = self.__class__.objects.filter(**filterVal).values(*fieldsLst).get()
            else :
                obj = self.__class__.objects.filter(**filterVal).get()        
        return obj
    
    def GetCount(self,filterVal,excludeVal=None):
        cnt = 0
        if excludeVal : 
            cnt = self.__class__.objects.filter(**filterVal).exclude(**excludeVal).count()
        else :
            cnt = self.__class__.objects.filter(**filterVal).count()
        return cnt

    def GetAll(self, filterVal, fieldsLst = None, isFltrQLst = False, orderby =None, startIndx = None,pageSize = None) :
        queryOb = None
        lst = None
        
        if isFltrQLst :
            queryOb =self.__class__.objects.filter(filterVal)
        else :
            queryOb =self.__class__.objects.filter(**filterVal)
        
        if fieldsLst :
            queryOb  = queryOb.values(*fieldsLst)
        
        if orderby :
            queryOb = queryOb.order_by(orderby)
        
        if pageSize :
            lst = queryOb.all()[startIndx:pageSize]
        else:
            lst = queryOb.all()
        
        return lst


class TMSettingsDetails(m.Model) :
    Id = m.BigAutoField(primary_key=True)
    ModuleId = m.CharField(max_length=500,null=False)
    AssignmentId = m.CharField(max_length=500,null=False)
    MaxStudents = m.IntegerField(null=False)
    PollingResult = m.CharField(max_length=250,null=False)
    TimeLimit = m.IntegerField(null=False)
    TimeLimitUnit = m.CharField(max_length=50,null=False)
    TeamScore = m.IntegerField(null=False)
    StudentScore = m.IntegerField(null=False)
    
    class Meta :
        db_table ='tmsettingsdetails'
    
    def CreateObject(self,valObj):
        res = self.__class__.objects.create(ModuleId = valObj["ModuleId"],
                                            AssignmentId = valObj["AssignmentId"],
                                            MaxStudents = valObj["MaxStudents"],
                                            PollingResult = valObj["PollingResult"],
                                            TimeLimit = valObj["TimeLimit"],
                                            TimeLimitUnit = valObj["TimeLimitUnit"],
                                            TeamScore = valObj["TeamScore"],
                                            StudentScore = valObj["StudentScore"])
        return res
    
    def GetCount(self,filterVal,excludeVal=None):
        cnt = 0
        if excludeVal : 
            cnt = self.__class__.objects.filter(**filterVal).exclude(**excludeVal).count()
        else :
            cnt = self.__class__.objects.filter(**filterVal).count()
        return cnt

    def GetObject(self,filterVal,fieldsLst=None):
        cnt = self.__class__.objects.filter(**filterVal).count()
        obj = None
        if cnt > 0 :
            if fieldsLst :
                obj = self.__class__.objects.filter(**filterVal).values(*fieldsLst).get()
            else :
                obj = self.__class__.objects.filter(**filterVal).get()        
        return obj
        
    def GetAll(self, filterVal, fieldsLst = None, isFltrQLst = False, orderby =None, startIndx = None,pageSize = None) :
        queryOb = None
        lst = None
        
        if isFltrQLst :
            queryOb =self.__class__.objects.filter(filterVal)
        else :
            queryOb =self.__class__.objects.filter(**filterVal)
        
        if fieldsLst :
            queryOb  = queryOb.values(*fieldsLst)
        
        if orderby :
            queryOb = queryOb.order_by(orderby)
        
        if pageSize :
            lst = queryOb.all()[startIndx:pageSize]
        else:
            lst = queryOb.all()
        
        return lst

class TMTeamAssignments(m.Model):
    Id = m.BigAutoField(primary_key=True)
    ModuleId = m.CharField(max_length=500,null=False)
    AssignmentId = m.CharField(max_length=500,null=False)
    TeamId = m.BigIntegerField(null=False)
    IsTimerStarted = m.PositiveSmallIntegerField(null=True,default=0)
    TimerDate = m.DateTimeField(null=True)
    TeamScore = m.DecimalField(null=True,max_digits=15, decimal_places=5)
    QuestionId= m.BigIntegerField(null=True)
    
    class Meta :
        db_table ='tmteamassignments'
    
    def CreateObject(self,valObj):
        res = self.__class__.objects.create(ModuleId = valObj["ModuleId"],
                                            AssignmentId = valObj["AssignmentId"],
                                            TeamId = valObj["TeamId"])
        return res
    
    def UpdateObject(self,filterVal,updateVal):
        usr = None    
        cnt = self.__class__.objects.filter(**filterVal).count()
        if cnt > 0 :
            usr = self.__class__.objects.filter(**filterVal).update(**updateVal)
            return usr
    
    def GetObject(self,filterVal,fieldsLst=None):
        cnt = self.__class__.objects.filter(**filterVal).count()
        obj = None
        if cnt > 0 :
            if fieldsLst :
                obj = self.__class__.objects.filter(**filterVal).values(*fieldsLst).get()
            else :
                obj = self.__class__.objects.filter(**filterVal).get()        
        return obj
    
    def GetCount(self,filterVal,excludeVal=None):
        cnt = 0
        if excludeVal : 
            cnt = self.__class__.objects.filter(**filterVal).exclude(**excludeVal).count()
        else :
            cnt = self.__class__.objects.filter(**filterVal).count()
        return cnt

class TMStudentScore(m.Model):
    Id = m.BigAutoField(primary_key=True)
    ModuleId = m.CharField(max_length=500,null=False)
    AssignmentId = m.CharField(max_length=500,null=False)
    StudentId = m.BigIntegerField(null=False)
    DoNotShowMsgAgain = m.PositiveSmallIntegerField(default=0)
    Score = m.DecimalField(null=True,max_digits=15, decimal_places=5)
    
    class Meta :
        db_table ='tmstudentscore'
    
    def CreateObject(self,valObj):
        res = self.__class__.objects.create(ModuleId = valObj["ModuleId"],
                                            AssignmentId = valObj["AssignmentId"],
                                            StudentId = valObj["StudentId"],
                                            DoNotShowMsgAgain = valObj["DoNotShowMsgAgain"])
        return res
    
    def UpdateObject(self,filterVal,updateVal):
        usr = None    
        cnt = self.__class__.objects.filter(**filterVal).count()
        if cnt > 0 :
            usr = self.__class__.objects.filter(**filterVal).update(**updateVal)
            return usr
    
    def GetObject(self,filterVal,fieldsLst=None):
        cnt = self.__class__.objects.filter(**filterVal).count()
        obj = None
        if cnt > 0 :
            if fieldsLst :
                obj = self.__class__.objects.filter(**filterVal).values(*fieldsLst).get()
            else :
                obj = self.__class__.objects.filter(**filterVal).get()        
        return obj
    
class TMStudQuestionResponse(m.Model) :
    Id = m.BigAutoField(primary_key=True)
    TeamId = m.BigIntegerField(null=False)
    StudentId = m.BigIntegerField(null=False)
    ModuleId = m.CharField(max_length=500,null=False)
    AssignmentId = m.CharField(max_length=500,null=False)
    QuestionId = m.BigIntegerField(null=False)
    SelectedOption = m.CharField(max_length=50,null=False)
    IsQuestionAnswered = m.PositiveSmallIntegerField()
    IsCorrect = m.PositiveSmallIntegerField()

    class Meta :
        db_table ='tmstudquestionsresponse'
    
    def CreateObject(self,valObj):
        res = self.__class__.objects.create(TeamId = valObj["TeamId"],
                                            StudentId = valObj["StudentId"],
                                            ModuleId = valObj["ModuleId"],
                                            AssignmentId = valObj["AssignmentId"],
                                            QuestionId = valObj["QuestionId"],
                                            SelectedOption = valObj["SelectedOption"],
                                            IsQuestionAnswered = valObj["IsQuestionAnswered"],
                                            IsCorrect = valObj["IsCorrect"])
        return res
    
    def GetCount(self,filterVal,excludeVal=None):
        cnt = 0
        if excludeVal : 
            cnt = self.__class__.objects.filter(**filterVal).exclude(**excludeVal).count()
        else :
            cnt = self.__class__.objects.filter(**filterVal).count()
        return cnt
    
    def GetAll(self, filterVal, fieldsLst = None, isFltrQLst = False, orderby =None, startIndx = None,pageSize = None) :
        queryOb = None
        lst = None
        
        if isFltrQLst :
            queryOb =self.__class__.objects.filter(filterVal)
        else :
            queryOb =self.__class__.objects.filter(**filterVal)
        
        if fieldsLst :
            queryOb  = queryOb.values(*fieldsLst)
        
        if orderby :
            queryOb = queryOb.order_by(orderby)
        
        if pageSize :
            lst = queryOb.all()[startIndx:pageSize]
        else:
            lst = queryOb.all()
        
        return lst

class CommonSPData(m.Model):
    Id = m.BigIntegerField(primary_key=True)
    Column1 = m.TextField()        
    Column2 = m.CharField(max_length=100,null=True)

