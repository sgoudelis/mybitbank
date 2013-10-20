from django.conf.urls import patterns, url

from transfer import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^send/', views.send, name='send'),
    url(r'^(?P<selected_currency>\w+)/', views.index, name='transfer'),
)