from django.conf.urls import patterns, url

from accounts import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add, name='add'),
    url(r'^create/$', views.create, name='create'),
    url(r'^details/(?P<account_address>\w+)/$', views.details, name='details'),
    url(r'^details/(?P<account_address>\w+)/(?P<page>\d+)/$', views.details, name='details'),
    url(r'^setaddressalias/$', views.setAddressAlias, name='set_address_alias'),
    url(r'^createnewaddress/(?P<old_address>\w+)/$', views.createNewAddress, name='create_new_address'),
)