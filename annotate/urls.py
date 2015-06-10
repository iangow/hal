from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^mirror/', include('mirror.urls')),
    url(r'^highlight', 'highlighter.views.highlight', name='highlight'),
)
