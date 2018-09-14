from django.conf.urls import *
from econ.ue.views import *
from econ.ue import fred

logger = logging.getLogger('fred_ue')

logger.info("Starting DAEMON")
FRED_DEAMON = fred.FredStartup(settings.DATABASES['default'])
logger.info("run count %d"%fred.runcount)

urlpatterns = patterns('',
    
    url(r'^getState$', getUEState),
    url(r'^startLevel$', startUELevel),    
    url(r'^completeLevel$', saveUELevel),
    url(r'^saveSettings$', saveUESettings),
    url(r'^getSettings$', getUESettings),
    #url(r'^quitLevel$', quitUELevel),
    url(r'^saveCustomData', saveUECustomData),
    url(r'^restart', restart),
    url(r'^getAggregates', getAggregates),
    url(r'^getStudents', getStudents),    
    url(r'^getStudentData', getStudentData),  
    url(r'getStateUnemploymentData', getStateUnemploymentData),
    url(r'getLaborParticipationData', getLaborParticipationData),  
    url(r'getCivilianUnemploymentData', getCivilianUnemploymentData),  
    url(r'getNaturalUnemploymentData', getNaturalUnemploymentData),      
)



# end of file


