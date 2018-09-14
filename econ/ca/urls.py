
from django.conf.urls import *
from econ.ca.views import *

urlpatterns = patterns('',
    
    url(r'^getState$', getState),
    url(r'^saveLevel$', saveLevel),
    url(r'^startLevel$', startLevel),
    #url(r'^quitLevel$', quitLevel),
    url(r'^getSetting$', getLevelSetting),
    url(r'^saveSetting$', saveLevelSetting),
    url(r'^getStudents$', getStudents),    
    url(r'^getStudentData', getStudentData),  
    url(r'^getAggregates', getAggregates),          
    url(r'^replay$', replay),
)

