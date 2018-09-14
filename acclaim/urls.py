from django.conf.urls import include, url,patterns
from django.contrib import admin

admin.autodiscover()
urlpatterns =  patterns('',
    # Examples:
    # url(r'^$', 'acclaim.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^DummyPage/$', 'acclaim.views.DummyPage', name='DummyPage'),
    url(r'^RevelResultReport/$', 'acclaim.views.RevelResultReport', name='RevelResultReport'),
    url(r'^getBadgeTemplates/$', 'acclaim.views.getBadgeTemplates', name='getBadgeTemplates'),
    url(r'^getOrgTokens/$', 'acclaim.views.getOrgTokens', name='getOrgTokens'),
    url(r'^issueBadgeToUser/$', 'acclaim.views.issueBadgeToUser', name='issueBadgeToUser'),
    url(r'^getOrganization/$', 'acclaim.views.getOrganization', name='getOrganization'),
    url(r'^getIssuers/$', 'acclaim.views.getIssuers', name='getIssuers'),
    url(r'^getgrantors/$', 'acclaim.views.getgrantors', name='getgrantors'),
    url(r'^getSelfInfo/$', 'acclaim.views.getSelfInfo', name='getSelfInfo'),    
    url(r'^sendemail/$', 'acclaim.views.sendemail', name='sendemail'),
    url(r'^showpage/$', 'acclaim.views.showpage', name='showpage'),
)
