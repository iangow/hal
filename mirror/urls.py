from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^/?$', views.home),
    url(r'^random$', views.random_filing),
    url(r'^highlight/(?P<folder>\d+/\d+)$', views.highlight, name='highlight'),
    url(r'^directorships/(?P<folder>\d+/\d+)/(?P<director_id>[^/]+)$', views.directorships, name='directorships'),
    url(r'^companies$', views.companies),
)
