from django.conf.urls import *
from econ.oppcost.views import *

urlpatterns = patterns(
    '',
    url(r'^getSettings/$', getOppCostSettings),
    url(r'^saveSettings/$', saveOppCostSettings),

    url(r'^getState/$', getOppCostState),
    url(r'^startLevel/$', startOppCostLevel),
    url(r'^completeLevel/$', saveOppCostLevel),
    url(r'^saveCustomData/$', saveOppCostCustomData),
    url(r'^restart/$', restart),
    url(r'^check_for_active_users/$', check_for_active_users),

    url(r'getAggregates/$', getAggregates),
    url(r'getStudentData/$', getStudentData),
    url(r'getStudents/$', getStudents),
)