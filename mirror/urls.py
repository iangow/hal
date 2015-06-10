from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^random$', views.random_filing),
    url(r'^(?P<folder>.*)$', views.mirror),
)
