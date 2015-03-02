from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^(?P<folder>\d+/\d+)/$', views.def_14a),
)
