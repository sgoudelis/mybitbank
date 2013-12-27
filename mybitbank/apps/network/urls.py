from django.conf.urls import patterns, url

import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<selected_provider_id>[0-9]+)/', views.index, name='index'),
)
