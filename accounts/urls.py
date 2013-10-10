from django.conf.urls import patterns, url

from accounts import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^add/', views.add, name='add'),
    url(r'^create/', views.create, name='create'),
)