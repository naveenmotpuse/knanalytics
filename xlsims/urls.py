from django.conf.urls import *
from views import *

urlpatterns = patterns('',
    
    url(r'^launch', launchSim),
    url(r'^service/getLaunchParams', getLaunchParams),
    url(r'^service/getState$', getState),    
    url(r'^service/getCustomData$', getCustomData),
    url(r'^service/saveCustomData', saveCustomData),
    url(r'^service/report$', report),
    url(r'^service/getStudents$', getStudents),
    url(r'^service/getStudentData$', getStudentData),
    url(r'^service/getClassStats$', getClassStats),
    url(r'^testing/mockLaunch', mockLaunch),
    url(r'^testing/login', loginEmulator),
    url(r'^testing/getSims', getSims),
    url(r'^testing/getMySession', getMySession),
    url(r'^testing/getSessions', getSessions),
    url(r'^testing/removeSession', removeSession),
    url(r'^get_sim_sessions', getDupSimSessions1),
    url(r'^postatmsimgrades', postatmsimgrades),
    url(r'^manualgradepostreport', manualgradepostreport),
)
