from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^add/', views.add, name='add'),
    url(r'^create/', views.create, name='create'),
    url(r'^delete/(?P<addressid>\d+)/', views.delete, name='delete'),
    url(r'^disable/(?P<addressid>\d+)/', views.toggleStatus, name='disable'),
)