import config
import generic
import datetime
from connections import connector
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geoip import GeoIP

current_section = 'peerinfo'

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
        peer['subver'] = peer['subver'].replace("/","")
        peer['in'] = generic.humanBytes(peer['bytesrecv'])
        peer['out'] = generic.humanBytes(peer['bytessent'])
        peer['lastsend'] = generic.twitterizeDate(peer['lastsend'])
        peer['lastrecv'] = generic.twitterizeDate(peer['lastrecv'])
        peer['conntime'] = generic.timeSince(peer['conntime'])
        peer['syncnode'] = peer['syncnode'] if 'syncnode' in peer else False
    
    currency_codes = []
    currency_names = {}
    currency_symbols = {}
    for currency in connector.config:
        currency_names[currency] = connector.config[currency]['currency_name']
        currency_symbols[currency] = connector.config[currency]['symbol']
        currency_codes.append(currency)
    
    
    currency_codes = sorted(currency_codes)
    
  
    page_title = _("peersinfo")
    context = {
               'globals': config.MainConfig['globals'], 
               'breadcrumbs': generic.buildBreadcrumbs(current_section, 'all'), 
               'system_errors': connector.errors,
               'page_title': page_title, 
               'page_sections': sections, 
               'request': request,
               'currency_codes': currency_codes,
               'currency_names': currency_names,
               'currency_symbols': currency_symbols,
               'selected_currency': selected_currency,
               'peers': peers
               }
    return render(request, 'peersinfo/index.html', context)

    