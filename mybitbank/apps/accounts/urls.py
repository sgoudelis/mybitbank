"""
The MIT License (MIT)

Copyright (c) 2016 Stratos Goudelis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

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
