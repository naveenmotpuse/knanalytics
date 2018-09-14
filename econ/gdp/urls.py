'''
Created on 19-July-2016

@author: naveen@knowdl.com
'''
from django.conf.urls import patterns, url
from econ.gdp.views import getFredData, pullFredData
 
urlpatterns = patterns(
 '',
 url(r'^get_fred_data/$', getFredData),
 url(r'^pull_fred_data/$', pullFredData),  
)






#end of file



