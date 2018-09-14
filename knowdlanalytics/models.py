
'''
Created on Apr 12, 2017
updated on Oct 25, 2017
@author: anuja
'''

from django.db import models as m

class ql_assignmentdetails(m.Model):
    Id =   m.AutoField(primary_key=True)
    Assignment_Id = m.TextField()
    QL_Id = m.TextField()
    QLTitle =m.TextField() 
    AssignmentTitle  =m.TextField()
    NumberOfAttempts = m.IntegerField()
    TargetPoints = m.FloatField() 
    AssignmentLocation = m.TextField() 
    Status =m.BooleanField()
    UpdatedBy = m.BigIntegerField(default=0) 
    ObjectiveDetails =m.TextField()    
    
    class Meta:
        db_table = 'ql_assignmentdetails'
        
class ql_assignmentadditionaldetails(m.Model):
    Id = m.AutoField(primary_key = True)    
    Assignment_Id = m.TextField()
    TotalScore = m.DecimalField(default=0, max_digits=10, decimal_places=2) 
    NumOfUsers = m.IntegerField(default=0)
    AdditionalField1 = m.TextField(default="")
    AdditionalField2 = m.TextField(default="")
    AdditionalField3 = m.TextField(default="")
    
    class Meta:
        db_table = 'ql_assignmentadditionaldetails'
    

class ql_masterquestions(m.Model) :
    Id = m.AutoField(primary_key=True)
    QL_Id = m.TextField()
    PageId = m.CharField(max_length=50) 
    QuestionId = m.CharField(max_length=100) 
    QuestionText = m.TextField()
    Options = m.TextField()
    TotalPoints = m.DecimalField(max_digits=10, decimal_places=2) 
    QuestionTitle = m.CharField(max_length=1000)
    AdditionalInfo = m.CharField(max_length=500) 
    Type = m.CharField(max_length=50)
    
    class Meta:
        db_table = 'ql_masterquestions'

class ql_masterattempts(m.Model):    
    Id = m.AutoField(primary_key=True) 
    Student_Id = m.TextField()
    Assignment_Id = m.TextField()
    QL_Id = m.TextField()
    StudentName = m.TextField()
    AssignmentTitle = m.TextField()
    Role = m.TextField()
    StartDate = m.DateTimeField()
    EndDate = m.DateTimeField()
    CompletionStatus = m.TextField() 
    TimeSpent =m.DecimalField(max_digits=10, decimal_places=2)
    Score = m.DecimalField(max_digits=10, decimal_places=2)
    Points = m.DecimalField(max_digits=10, decimal_places=2)
    AssignmentLocation = m.TextField()
    Session_Id = m.TextField()
    ReportStatus = m.TextField()
    
    class Meta:
        db_table = 'ql_masterattempts'
        
class ql_questionattemptdetails(m.Model):    
    Id = m.AutoField(primary_key=True) 
    MstAttemptId = m.BigIntegerField() 
    PageId = m.TextField() 
    QuestionId = m.TextField()
    SelOptionId = m.TextField()
    CorrectStatus = m.TextField()
    Score = m.DecimalField(max_digits=10, decimal_places=2)
    Points = m.DecimalField(max_digits=10, decimal_places=2)
    TimeSpent = m.DecimalField(max_digits=10, decimal_places=2)
    AdditionalInfo = m.TextField()
    
    class Meta:
        db_table = 'ql_questionattemptdetails'

#Anu 25-oct-2017 for QLInteractionController
class tbl_LogEntries(m.Model) :
    Id = m.AutoField(primary_key=True)        
    LogString  = m.TextField()         #[StringLength(Int32.MaxValue)]
    LogDate = m.DateTimeField() 

    class Meta:
        db_table = 'tbl_LogEntries'
        
        




#end of file.