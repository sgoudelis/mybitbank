from django.conf.urls import patterns, url

import views

urlpatterns = patterns('accounts',
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add, name='add'),
    url(r'^create/$', views.create, name='create'),
    url(r'^details/(?P<provider_id>\w+)/(?P<account_identifier>\w+)/transactions/(?P<page>\d+)/$', views.details_with_transactions, name='details_with_transactions'),
    url(r'^details/(?P<provider_id>\w+)/(?P<account_identifier>\w+)/addresses/(?P<page>\d+)/$', views.details_with_addresses, name='details_with_addresses'),
    url(r'^setaddressalias/$', views.setAddressAlias, name='set_address_alias'),
    url(r'^createnewaddress/(?P<provider_id>\w+)/(?P<account_identifier>\w+)/$', views.createNewAddress, name='create_new_address'),
)
