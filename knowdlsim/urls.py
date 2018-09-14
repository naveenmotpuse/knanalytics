





'''
Created on 11-dec-2017

@author: vinod@knowdl.com
'''
from django.conf.urls import patterns, url
from knowdlsim.views import k_copy, k_create, k_delete, k_get, k_post_grade, k_update,\
    k_getAll, k_deleteAll,k_validate_token, k_getHeaders , \
    k_saveAssignmentSettings, k_getAssignmentSettings, k_process,\
    k_getAssignmentData, getAttemptCount, k_get_user,k_get_all_users, getAttemptData, k_launch, RevelAnalytics,RevelAnalyticsDetails,\
    RevelClassReport,RevelOutcomes,RevelOverview,RevelStudentReport,\
    RevelTrendsAcrossQues,RevelTrendsAcrossQuesDetails, RevelIndivisualStudentReport,\
    RevelResultReport

urlpatterns = patterns(
    '', 
    url(r'^launch/(?P<course_id>[\w\-]+)/(?P<assignment_id>[\w\-]+)/', k_launch),
    url(r'^assignments/get/(?P<course_id>[-\w]+)/(?P<assignment_id>[-\w]+)/', k_get),
    url(r'^assignments/getall/(?P<course_id>[-\w]+)/', k_getAll),
    url(r'^assignments/delete/(?P<course_id>[-\w]+)/(?P<assignment_id>[-\w]+)/', k_delete),    
    url(r'^assignments/deleteall/(?P<course_id>[-\w]+)/', k_deleteAll),    
    url(r'^assignments/create/', k_create),
    url(r'^assignments/update/', k_update),    
    url(r'^assignments/copy/', k_copy),
    url(r'^assignments/post_grade/', k_post_grade),    
    url(r'^assignments/get_user/(?P<course_id>[-\w]+)/', k_get_user),
    url(r'^assignments/get_all_user/(?P<course_id>[-\w]+)/', k_get_all_users),
    url(r'^assignments/validatetoken/(?P<identity_id>[-\w]+)/', k_validate_token),    
    url(r'^assignments/getheaders/', k_getHeaders),    
    url(r'^assignments/save_settings/(?P<course_id>[-\w]+)/(?P<assignment_id>[-\w]+)/(?P<template_id>[-\w]+)', k_saveAssignmentSettings),    
    url(r'^assignments/get_settings/(?P<course_id>[-\w]+)/(?P<assignment_id>[-\w]+)/(?P<template_id>[-\w]+)/', k_getAssignmentSettings),
    url(r'^assignments/process/(?P<course_id>[-\w]+)/(?P<assignment_id>[-\w]+)/(?P<template_id>[-\w]+)/(?P<command>[-\w]+)/', k_process),
    url(r'^assignments/get_attempt_count/(?P<course_id>[-\w]+)/(?P<assignment_id>[-\w]+)/(?P<template_id>[-\w]+)/(?P<student_id>[-\w]+)/', getAttemptCount),
    url(r'^assignments/get_attempt_data/(?P<course_id>[-\w]+)/(?P<assignment_id>[-\w]+)/(?P<template_id>[-\w]+)/(?P<student_id>[-\w]+)/', getAttemptData),
    url(r'^assignments/get_assignment_data/', k_getAssignmentData),    

    url(r'^revelanalytics/RevelTrendsAcrossQues/$', RevelTrendsAcrossQues),
    url(r'^revelanalytics/RevelTrendsAcrossQuesDetails/$', RevelTrendsAcrossQuesDetails),    
    url(r'^revelanalytics/RevelAnalytics/$', RevelAnalytics),
    url(r'^revelanalytics/RevelAnalyticsDetails/$', RevelAnalyticsDetails),
    url(r'^revelanalytics/RevelOverview/$', RevelOverview),
    url(r'^revelanalytics/RevelClassReport/$', RevelClassReport),
    url(r'^revelanalytics/RevelStudentReport/$', RevelStudentReport),
    url(r'^revelanalytics/RevelIndivisualStudentReport/$', RevelIndivisualStudentReport),
    url(r'^revelanalytics/RevelOutcomes/$', RevelOutcomes),
    url(r'^revelanalytics/RevelResultReport/$',RevelResultReport),
    url(r'^sendemail/$',sendemail),
    url(r'^showpage/$',showpage),
)
