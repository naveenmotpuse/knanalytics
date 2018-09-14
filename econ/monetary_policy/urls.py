from django.conf.urls import patterns, url
from econ.monetary_policy.views import get_indicators, check_indicators,\
 saveMPSettings, getMPSettings, restart, getAggregates, getStudents,\
 getStudentData, getMPState, startMPLevel, saveMPLevel, saveMPCustomData,\
 get_economic_situation, get_question, check_answer, check_l3_context,\
 getFredData, check_for_active_users, check_level4_context, getGraphEvents,\
 getRecessionPeriods

urlpatterns = patterns(
 '',
 url(r'^saveSettings/$', saveMPSettings),
 url(r'^getSettings/$', getMPSettings),

 url(r'^getState/$', getMPState),
 url(r'^saveState/$', saveMPCustomData),
 url(r'^startLevel/$', startMPLevel),
 url(r'^completeLevel/$', saveMPLevel),
 url(r'^restart/$', restart),

 url(r'^getAggregates/$', getAggregates),
 url(r'^getStudents/$', getStudents),
 url(r'^getStudentData/$', getStudentData),
 url(r'^check_for_active_users/$', check_for_active_users),

 url(r'^get_indicators/$', get_indicators),
 url(r'^check_indicators/$', check_indicators),

 url(r'^get_question/$', get_question),
 url(r'^check_answer/$', check_answer),
 url(r'^check_level4_context/$', check_level4_context),

 url(r'^get_situation/$', get_economic_situation),
 url(r'^check_context/$', check_l3_context),

 url(r'^get_fred_data/$', getFredData),
 url(r'^get_graph_events/$', getGraphEvents),
 url(r'^get_recession_periods/$', getRecessionPeriods),
)





