


'''
Created on Apr 20, 2017

@author: anuja
'''
class RevelQuestionDetailReportView :
    def __init__(self):
        self.Results = [] #List<RevelQuestionDetailReport>  
        self.PageIndex = 0
        self.RecordCount = 0
        self.PageSize = 5
        self.AverageScore = 0.00
        self.AverageCompleted = 0.00
        self.MedianScore = 0.00
        
class RevelQuestionDetailReport :
    def __init__(self):
        self.Id = "" 
        self.Text = ""        
        self.Options = [] # List<RevelOptionReport> 
        self.ForGraph = "" 
        self.NumberOfTimesAnswered = 0 
        self.QuestionTitle = ""
        self.Presented = "" 
        self.Points = ""
        self.TotalAttempted = "" 
        self.QuestionAttempted ="" 
        self.AverageScorePercent ="" 
        self.Students = [] # List<RevelStudentDetails>
        self.OptionAlignment = "" 
        self.OccurenceNo ="" 

class RevelStudentDetails :
    def __init__(self):
        self.Id = "" 
        self.Name = "" 
        self.Points = ""         
        self.MasterAttemptId = 0 
        self.Score = 0.0 
        self.CompletionStatus = "" 
        self.Questions = []  # List<RevelQuestionForStudentReport>
        self.Attempts = [] # List<RevelStudentAttempt>

class RevelOptionReport :
    def __init__(self):
        self.Id = "" 
        self.Text = "" 
        self.Points = "" 
        self.Status = "" 
        self.Image = "" 
        self.NumberOfTimesAnswered = 0 
        self.Percent = "" 
        self.PointsImage = "" 

class RevelQuestionForStudentReport :
    def __init__(self):
        self.Id = ""       
        self.TotalPoints = 0
        self.PointsObtained = 0
        self.SelectedOption =""
        self.PointsImage =""
    
class RevelStudentAttempt :
    def __init__(self):
        self.SessionId = "" 
        self.Score = None   # Nullable<double> 
        self.AttemptNo = 0        
    
class RevelStudentReportView :
    def __init__(self):
        self.Results = [] # List<RevelStudentDetails> 
        self.QuestionsDetails = [] # List<RevelQuestionMasterForStudentReport>
        self.AverageScore = 0.00
        self.PageIndex = -1
        self.RecordCount = 0
        self.PageSize = 5
    
class RevelQuestionMasterForStudentReport :
    def __init__(self):
        self.Id = ""   
        self.Text = "" 
        self.QuestionTitle = ""
        self.Options = [] # List<RevelOption> 
        self.OptionAlignment = ""
        self.OccurenceNo = ""

class RevelOption :
    def __init__(self):
        self.Id = ""
        self.Text = ""
        self.Points = ""
        self.Status = ""
        self.Img = ""
        self.FeedbackText = ""
        self.rolloverImg = ""

class RevelOutcomesModel :
    def __init__(self):
        self.TotalAttempted = 0
        self.Description = ""
        self.Title = ""
        self.ChartData = ""
        self.Objectives = [] # List<RevelOutcomeObjectiveModel> 
    

class RevelOutcomeObjectiveModel :
    def __init__(self):
        self.Id = ""
        self.Name = ""
        self.Title = ""
        self.AverageScore = 0.00
        self.PresentedCount = 0 
        self.Questions = []  #List<RevelOutcomesQuestionModel>
    

class RevelOutcomesQuestionModel :
    def __init__(self):
        self.QuestionId = ""
        self.QuestionTitle = ""
        self.QuestionText = ""
        self.AverageScore = 0.00
        self.PresentedCount = 0
    
    
    
    
    
    



#end of file
