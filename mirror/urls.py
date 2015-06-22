from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^/?$', views.home),
    url(r'^random$', views.random_filing),
    url(r'^highlight/(?P<folder>\d+/\d+)$', 'mirror.views.highlight', name='highlight'),
    url(r'^filing/(?P<folder>\d+/\d+)$', views.mirror, name='filing'),
)
