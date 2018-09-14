'''
Created on Apr 20, 2017

@author: anuja
'''
class QLQuestionDetailReportView :
    def __init__(self):
        self.Results = [] #List<QLQuestionDetailReport>  
        self.PageIndex = 0
        self.RecordCount = 0
        self.PageSize = 5
        self.AverageScore = 0.00
        self.AverageCompleted = 0.00
        self.MedianScore = 0.00
        
class QLQuestionDetailReport :
    def __init__(self):
        self.Id = "" 
        self.Text = ""        
        self.Options = [] # List<QlOptionReport> 
        self.ForGraph = "" 
        self.NumberOfTimesAnswered = 0 
        self.QuestionTitle = ""
        self.Presented = "" 
        self.Points = ""
        self.TotalAttempted = "" 
        self.QuestionAttempted ="" 
        self.AverageScorePercent ="" 
        self.Students = [] # List<QLStudentDetails>
        self.OptionAlignment = "" 
        self.OccurenceNo ="" 

class QLStudentDetails :
    def __init__(self):
        self.Id = "" 
        self.Name = "" 
        self.Points = ""         
        self.MasterAttemptId = 0 
        self.Score = 0.0 
        self.CompletionStatus = "" 
        self.Questions = []  # List<QLQuestionForStudentReport>
        self.Attempts = [] # List<QLStudentAttempt>

class QlOptionReport :
    def __init__(self):
        self.Id = "" 
        self.Text = "" 
        self.Points = "" 
        self.Status = "" 
        self.Image = "" 
        self.NumberOfTimesAnswered = 0 
        self.Percent = "" 
        self.PointsImage = "" 

class QLQuestionForStudentReport :
    def __init__(self):
        self.Id = ""       
        self.TotalPoints = 0
        self.PointsObtained = 0
        self.SelectedOption =""
        self.PointsImage =""
    
class QLStudentAttempt :
    def __init__(self):
        self.SessionId = "" 
        self.Score = None   # Nullable<double> 
        self.AttemptNo = 0        
    
class QLStudentReportView :
    def __init__(self):
        self.Results = [] # List<QLStudentDetails> 
        self.QuestionsDetails = [] # List<QlQuestionMasterForStudentReport>
        self.AverageScore = 0.00
        self.PageIndex = -1
        self.RecordCount = 0
        self.PageSize = 5
    
class QlQuestionMasterForStudentReport :
    def __init__(self):
        self.Id = ""   
        self.Text = "" 
        self.QuestionTitle = ""
        self.Options = [] # List<QlOption> 
        self.OptionAlignment = ""
        self.OccurenceNo = ""

class QlOption :
    def __init__(self):
        self.Id = ""
        self.Text = ""
        self.Points = ""
        self.Status = ""
        self.Img = ""
        self.FeedbackText = ""
        self.rolloverImg = ""

class QLOutcomesModel :
    def __init__(self):
        self.TotalAttempted = 0
        self.Description = ""
        self.Title = ""
        self.ChartData = ""
        self.Objectives = [] # List<QLOutcomeObjectiveModel> 
    

class QLOutcomeObjectiveModel :
    def __init__(self):
        self.Id = ""
        self.Name = ""
        self.Title = ""
        self.AverageScore = 0.00
        self.PresentedCount = 0 
        self.Questions = []  #List<QLOutcomesQuestionModel>
    

class QLOutcomesQuestionModel :
    def __init__(self):
        self.QuestionId = ""
        self.QuestionTitle = ""
        self.QuestionText = ""
        self.AverageScore = 0.00
        self.PresentedCount = 0
    
    
    
    
    
    



#end of file.