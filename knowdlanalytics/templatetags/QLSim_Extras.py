'''
Created on Apr 24, 2017

@author: anuja
'''

from django import template
register = template.Library()

@register.assignment_tag
def optionSelStatus(stat):
    cssClass = ""
    statusString = ""
    
    if stat == "incorrect" :
        cssClass = "incorrect"
        statusString = "Wrong Answer"
    elif stat == "correct" :
        cssClass = "correct"
        statusString = "Correct Answer"
    elif stat == "partial" :
        cssClass= "partialcorrect"
        statusString = "Partial Credit Answer"
    return [statusString, cssClass]
#'cssClass': cssClass, 

@register.inclusion_tag('QLSimAnalyticsDetails.html', takes_context=True)
def show_QLSimAnalyticsDetails(context):    
    #ASGN = request.GET.get('ASGN', None)        
    return { "AssignmentTitle" : ""}

@register.assignment_tag
def FindQuestionInArray(QuestionsDetails, Id):
    questionDetail = None
    for qsn in QuestionsDetails:
        if qsn.Id == Id :                           
            questionDetail = qsn
            break
    return questionDetail

@register.assignment_tag
def AddPointImageOrNot(question, option):
    imgsrc = ""
    feedBackText = ""
    pointsImage = ""
    if option["Id"] == question.SelectedOption :
        imgsrc = option["rolloverImg"]
        feedBackText = option["FeedbackText"]
        pointsImage =  question.PointsImage
        addPointImage = True
    else :
        imgsrc = option["Img"]
        addPointImage = False
    
    return { "imgsrc" : imgsrc, "addPointImage" : addPointImage, "feedBackText" :feedBackText, "pointsImage" : pointsImage }
