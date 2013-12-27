from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<selected_provider_id>\d+)/(?P<page>\d+)/$', views.index, name='index'),
    url(r'^details/(?P<provider_id>[0-9]+)/(?P<txid>\w+)/$', views.transactionDetails, name='details'),
)
