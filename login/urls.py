from django.conf.urls import patterns, url

from login import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^process/', views.processLogin, name='processLogin'),
    url(r'^logout/', views.processLogout, name='processLogout'),
)