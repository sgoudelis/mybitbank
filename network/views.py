import config
import generic
import datetime
from connections import connector
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geoip import GeoIP
import json
import urllib2

current_section = 'network'

@login_required
def index(request, selected_currency=sorted(connector.config.keys())[0]):
    '''
    Handler for the accounts
    '''
    sections = generic.getSiteSections(current_section)
    
    g = GeoIP()
    peers = generic.getPeerInfo(connector, selected_currency)
    for peer in peers:
        info = g.city(peer['addr'].partition(':')[0])
        peer['country'] = info['country_name']
        peer['city'] =  info['city'] if info['city'] != None else 'N/A'
        peer['lat'] =  info['latitude'];
        peer['lon'] =  info['longitude'];
        peer['subver'] = peer['subver'].replace("/","")
        peer['in'] = generic.humanBytes(peer['bytesrecv']) if 'bytesrecv' in peer else 'N/A'
        peer['out'] = generic.humanBytes(peer['bytessent']) if 'bytessent' in peer else 'N/A'
        peer['lastsend'] = generic.twitterizeDate(peer['lastsend']) if 'lastsend' in peer else 'N/A'
        peer['lastrecv'] = generic.twitterizeDate(peer['lastrecv']) if 'lastrecv' in peer else 'N/A'
        peer['conntime'] = generic.timeSince(peer['conntime']) if 'conntime' in peer else 'N/A'
        peer['syncnode'] = peer['syncnode'] if 'syncnode' in peer else False
    
    currency_codes = []
    currency_names = {}
    currency_symbols = {}
    for currency in connector.config:
        currency_names[currency] = connector.config[currency]['currency_name']
        currency_symbols[currency] = connector.config[currency]['symbol']
        currency_codes.append(currency)
    
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
    
    page_title = _("Network")
    context = {
               'globals': config.MainConfig['globals'], 
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', currency_names[selected_currency]), 
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'page_title': page_title, 
               'page_sections': sections, 
               'request': request,
               'currency_codes': currency_codes,
               'currency_names': currency_names,
               'currency_symbols': currency_symbols,
               'selected_currency': selected_currency,
               'userinfo': userinfo,
               'peers': peers
               }
    return render(request, 'network/index.html', context)

    
