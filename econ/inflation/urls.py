from django.conf.urls import patterns, url

import econ.inflation.views as views

urlpatterns = patterns(
    '',
    url(r'^getInflationSettings/$', views.getInflationSettings),
    url(r'^saveInflationSettings/$', views.saveInflationSettings),

    url(r'^getState/$', views.getInflationState),
    url(r'^startLevel/$', views.startInflationLevel),
    url(r'^completeLevel/$', views.saveInflationLevel),
    url(r'^saveCustomData/$', views.saveInflationCustomData),
    url(r'^restart/$', views.restart),

    url(r'^getAggregates/$', views.getAggregates),
    url(r'^getStudents/$', views.getStudents),
    url(r'^getStudentData/$', views.getStudentData),

    url(r'^cpi/(?P<index_names>[\w,]+)$', views.getCpiData),
    url(r'^check_for_active_users/$', views.check_for_active_users)
)