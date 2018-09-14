"""knanalytics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

import django;
#import econ.ca.views

from django.conf.urls import patterns
from django.conf.urls import *
from gllaunch.views import *
from gldata.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
#from knowdlservice.views import k_launch

admin.autodiscover()
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^testvb/avbtoolLaunch/', vb_tool_launch),    
    #url(r'^app/index.html', simplelaunch),
    url(r'^econservice/gllaunch/echo_test/', echo_LTI_vars),
    url(r'^econservice/gllaunch/toolLaunch/', tool_launch),
    url(r'^econservice/econlaunch/echo_test/', echo_LTI_vars),
    url(r'^econservice/econlaunch/toolLaunch/', econ_tool_launch),
    url(r'^econservice/econlaunch/forceToolLaunch/', force_econ_tool_launch),

    url(r'^simLaunch/', include('xlsims.urls')),           
    
    #the following urls is for development and testing support, the Pearson server uses a url rewrite causing the xlsim/ portion to get cut off
    url(r'^xlsim/simLaunch/', include('xlsims.urls')),      
    # Examples:
    # url(r'^$', 'glservice.views.home', name='home'),
        
    url(r'^econservice/gldata/', include('gldata.urls')),
    url(r'^' + settings.DATA_URI + 'econservice/data/econ/ca/', include('econ.ca.urls')),
    url(r'^' + settings.DATA_URI + 'econservice/data/econ/ue/', include('econ.ue.urls')),
    url(r'^' + settings.DATA_URI + 'econservice/data/econ/oppcost/', include('econ.oppcost.urls')),
    url(r'^' + settings.DATA_URI + 'econservice/data/econ/inflation/', include('econ.inflation.urls')),
    # monetary_policy_url commented for time being. 07/14/2015
    url(r'^' + settings.DATA_URI + 'econservice/data/econ/monetary_policy/', include('econ.monetary_policy.urls')),
    #naveen@knowdl.com 15 April 2016
    url(r'^' + settings.DATA_URI + 'econservice/data/econ/common_services/', include('econ.common_services.urls')),
    #naveen@knowdl.com 19 July 2016
    url(r'^' + settings.DATA_URI + 'econservice/data/econ/gdp/', include('econ.gdp.urls')),
    
    #url(r'^simulator/', include('innovativeLaunch.urls')),
    #url(r'^xl/simulator/', include('innovativeLaunch.urls')),   
    
    url(r'^xl/admin/', include(admin.site.urls)),
    url(r'^' + settings.DATA_URI + 'version/', getVersion),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^acclaim/', include('acclaim.urls')),
    url(r'^media_library/',include('media_library.urls')),
    url(r'^importcsv/',include('importcsv.urls')),
    #url(r'^teamassignmenttool',include('teamassignmenttool.urls')),
)
