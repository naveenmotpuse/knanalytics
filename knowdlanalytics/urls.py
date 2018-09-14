from django.conf.urls import patterns, url

from knowdlanalytics.views import QLSimAnalytics,QLSimAnalyticsDetails,\
    QLSimClassReport,QLSimOutcomes,QLSimOverview,QLSimStudentReport,\
    QLSimTrendsAcrossQues,QLSimTrendsAcrossQuesDetails,GetLocQLString,\
    GetAssignmentsString, QLInteractionProcess, fGetAddData

urlpatterns = patterns('',   
   
    # Add the following line to link the root URL to the function myblog.views.index()
    url(r'^QLSimTrendsAcrossQues/$', QLSimTrendsAcrossQues),
    url(r'^QLSimTrendsAcrossQuesDetails/$', QLSimTrendsAcrossQuesDetails),    
    url(r'^QLSimAnalytics/$', QLSimAnalytics),
    url(r'^QLSimAnalyticsDetails/$', QLSimAnalyticsDetails),
    url(r'^QLSimOverview/$', QLSimOverview),
    url(r'^QLSimClassReport/$', QLSimClassReport),
    url(r'^QLSimStudentReport/$', QLSimStudentReport),
    url(r'^QLSimOutcomes/$', QLSimOutcomes),    
    url(r'^GetAssignmentsString/$', GetAssignmentsString),
    url(r'^GetLocQLString/$', GetLocQLString),
    #updated on Oct 25, 2017 Anu
    url(r'^QLInteractionProcess/$', QLInteractionProcess),
    url(r'^fGetAddData/$', fGetAddData),
    
    ## Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    ## Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls))
)









#end of file

