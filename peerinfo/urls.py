from django.conf.urls import patterns, url

from peerinfo import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<selected_currency>\w+)/', views.index, name='index'),
)