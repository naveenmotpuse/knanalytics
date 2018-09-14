from django.conf.urls import  url
#from LoginSystem.views import login_view

# Uncomment the next two lines to enable the admin:
from django.contrib import admin 

from . import views

admin.autodiscover()

app_name = 'teamassignmenttool'

urlpatterns = [
    url(r'showteamtable/$', views.showteamtable),
    url(r'createorupdateteam/$',views.createorupdateteam),
    url(r'addstudtoteam/$',views.addstudtoteam),
    url(r'getstudteamdetails/$',views.getstudteamdetails),
    url(r'addquestionresponse/$',views.addquestionresponse),
    url(r'checkquestionstatus/$',views.checkquestionstatus),
    url(r'testcall/$',views.testcall),
    url(r'calculateteamscore/$',views.calculateteamscore),
    url(r'donotdisplaymsgagain/$',views.donotdisplaymsgagain),
    url(r'getdonotdisplaymsgvalue/$',views.getdonotdisplaymsgvalue)
    ]


