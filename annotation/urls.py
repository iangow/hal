from django.conf.urls import url
import views

urlpatterns = [
    url(r'^annotations$', views.AnnotationC.as_view()),
    url(r'^annotations/(?P<pk>[0-9a-z]*)$', views.AnnotationRUD.as_view()),
]
