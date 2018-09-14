from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^getRequestedMediaJson', views.getRequestedMediaJson),
    url(r'^setRequestedMediaJson', views.setRequestedMediaJson),
    url(r'^getSaveAssignmentView', views.getSaveAssignmentView),
    url(r'^getAssignedMediaView', views.getAssignedMediaView),
    url(r'^getSearchMediaView', views.getSearchMediaView),
    url(r'^getFilterMediaView', views.getFilterMediaView),
    url(r'getEditMediaView', views.getEditMediaView),
)
