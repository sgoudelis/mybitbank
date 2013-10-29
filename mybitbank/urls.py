from django.conf.urls import patterns, include, url
from django.http.response import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
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
    url(r'^dashboard/', include('dashboard.urls', namespace="dashboard")),
    
    # accounts
    url(r'^accounts/', include('accounts.urls', namespace="accounts")),
    
    # addressbook
    url(r'^addressbook/', include('addressbook.urls', namespace="addressbook")),
    
    # transfer
    url(r'^transfer/', include('transfer.urls', namespace="transfer")),
    
    # transactions
    url(r'^transactions/', include('transactions.urls', namespace="transactions")),
    
    # login
    url(r'^login/', include('login.urls', namespace="login")),
    
    # peerinfo
    url(r'^peerinfo/', include('peerinfo.urls', namespace="peerinfo")),
    
    # language
    (r'^i18n/', include('django.conf.urls.i18n')),
)
