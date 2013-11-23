import config
import generic
import datetime
import json
import urllib2
from connections import connector
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geoip import GeoIP


current_section = 'network'

@login_required
def index(request, selected_provider_id=sorted(connector.config.keys())[0]):
    '''
    Handler for the accounts
    '''
    sections = generic.getSiteSections(current_section)
    selected_provider_id= int(selected_provider_id)
    
    g = GeoIP()
    notsupported = 0;
    peers = generic.getPeerInfo(connector, selected_provider_id)
    if 'error' in peers :
        peers = {}
        notsupported = 1
    else :
        for peer in peers:
            info = g.city(peer['addr'].partition(':')[0])
            peer['ip'] = peer['addr'].partition(':')[0]
            peer['port'] = peer['addr'].partition(':')[2]
            peer['country'] = info['country_name']
            peer['country_code'] = info['country_code']
            peer['city'] =  info['city'] if info['city'] != None else ''
            peer['lat'] =  info['latitude'];
            peer['lon'] =  info['longitude'];
            peer['subver'] = peer['subver'].replace("/","")
            peer['in'] = generic.humanBytes(peer['bytesrecv']) if 'bytesrecv' in peer else 'N/A'
            peer['out'] = generic.humanBytes(peer['bytessent']) if 'bytessent' in peer else 'N/A'
            peer['lastsend'] = generic.twitterizeDate(peer['lastsend']) if 'lastsend' in peer else 'N/A'
            peer['lastrecv'] = generic.twitterizeDate(peer['lastrecv']) if 'lastrecv' in peer else 'N/A'
            peer['conntime'] = generic.timeSince(peer['conntime']) if 'conntime' in peer else 'N/A'
            peer['syncnode'] = peer['syncnode'] if 'syncnode' in peer else False
    
    currency_codes = {}
    currency_names = {}
    currency_symbols = {}
    for provider_id in connector.config:
        currency_names[provider_id] = connector.config[provider_id]['name']
        currency_symbols[provider_id] = connector.config[provider_id]['symbol']
        currency_codes[provider_id] = connector.config[provider_id]['currency']
    
    currency_codes = sorted(currency_codes)
    
    ip = '127.0.0.1'
    try :
        '''
        We need some cache here or another way to detect *coind bind address
        '''
        data = urllib2.urlopen('http://wtfismyip.com/json')
        data = json.load(data)
        ip = data['YourFuckingIPAddress']
    except (urllib2.URLError, urllib2.HTTPError, TypeError) as e :
        print e
    
    info =  g.city(ip)
    userinfo = {}
    userinfo['lat'] = info['latitude'] if info is not None  else 1
    userinfo['lon'] = info['longitude'] if info is not None else 1
    
    print currency_names
    page_title = _("Network")
    context = {
               'globals': config.MainConfig['globals'], 
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', currency_names[selected_provider_id]), 
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'page_title': page_title, 
               'page_sections': sections, 
               'request': request,
               'currency_codes': currency_codes,
               'currency_names': currency_names,
               'currency_symbols': currency_symbols,
               'selected_provider_id': selected_provider_id,
               'userinfo': userinfo,
               'peers': peers,
               'notsupported': notsupported
               }
    return render(request, 'network/index.html', context)

    
