from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mybitbank.views.home', name='home'),
    # url(r'^mybitbank/', include('mybitbank.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # dashboard
    url(r'^dashboard/', include('dashboard.urls', namespace="dashboard")),
    
    # accounts
    url(r'^accounts/', include('accounts.urls', namespace="accounts")),
)
