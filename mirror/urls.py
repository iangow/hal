from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'random$', views.random_filing),
    url(r'highlight/(?P<folder>.*)$', 'mirror.views.highlight', name='highlight'),
    url(r'filing/(?P<folder>.*)$', views.mirror, name='filing'),
)
