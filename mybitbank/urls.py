from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http.response import HttpResponseRedirect


# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', lambda r : HttpResponseRedirect('login/')),
    # url(r'^mybitbank/', include('mybitbank.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # dashboard
    url(r'^dashboard/', include('mybitbank.apps.dashboard.urls', namespace="dashboard")),
    
    # accounts
    url(r'^accounts/', include('mybitbank.apps.accounts.urls', namespace="accounts")),
    
    # addressbook
    url(r'^addressbook/', include('mybitbank.apps.addressbook.urls', namespace="addressbook")),
    
    # transfer
    url(r'^transfer/', include('mybitbank.apps.transfer.urls', namespace="transfer")),
    
    # transactions
    url(r'^transactions/', include('mybitbank.apps.transactions.urls', namespace="transactions")),
    
    # login
    url(r'^login/', include('mybitbank.apps.login.urls', namespace="login")),
    
    # network
    url(r'^network/', include('mybitbank.apps.network.urls', namespace="network")),
    
    # language
    (r'^i18n/', include('django.conf.urls.i18n')),
)
