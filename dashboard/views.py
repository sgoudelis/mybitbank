import config
import generic
import calendar
import urllib2
from connections import connector
from events.models import Events
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    '''
    Handler for the dashboard main page
    '''
    currect_section = 'dashboard'
    
    balances = connector.getbalance()
    transactions_by_currency = connector.listalltransactions(limit=20, start=0)
    transactions = []
    for provider_id in transactions_by_currency:
        for transaction in transactions_by_currency[provider_id]:
            if transaction['category'] != 'move':
                transaction['currency'] = connector.config[provider_id]['currency']
                transactions.append(transaction)
    
    # sort result
    transactions = sorted(transactions, key=lambda k: k.get('time',0), reverse=True)
    
    # get only 10 transactions
    transactions = transactions[0:10]
    
    for transaction in transactions:
        transaction['currency_symbol'] = generic.getCurrencySymbol(transaction['currency'].lower())
        if transaction['category'] == 'receive':
            transaction['source_address'] = transaction.get('details', {}).get('sender_address', '(no sender address)')
            transaction['destination_address'] = transaction['address']
            transaction['icon'] = 'glyphicon-circle-arrow-down'
        elif transaction['category'] == 'send':
            transaction['source_addresses'] = connector.getaddressesbyaccount(transaction['account'], transaction['provider_id'])
            transaction['destination_address'] = transaction['address']
            transaction['icon'] = 'glyphicon-circle-arrow-up'
        elif transaction['category'] == 'move':
            transaction['source_address'] = connector.getaddressesbyaccount(transaction['account'], transaction['provider_id'])
            transaction['destination_address'] = connector.getaddressesbyaccount(transaction['otheraccount'], transaction['provider_id'])
            if not transaction['account']:
                transaction['alternative_name'] = '(default account)'
            transaction['icon'] = 'glyphicon-circle-arrow-right'

    currency_codes = {}
    currency_names = {}
    currency_symbols = {}
    for provider_id in connector.config:
        currency_names[provider_id] = connector.config[provider_id]['name']
        currency_symbols[provider_id] = connector.config[provider_id]['symbol']
        currency_codes[provider_id] = connector.config[provider_id]['currency']
    
    # events
    list_of_events = Events.objects.all().order_by('-entered')[:10]  
    for single_event in list_of_events:
        timestamp = calendar.timegm(single_event.entered.timetuple())
        single_event.entered_pretty = generic.twitterizeDate(timestamp)
    
    page_title = "Dashboard"
    sections = generic.getSiteSections('dashboard')
    context = {
               'globals': config.MainConfig['globals'], 
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'request': request,
               'breadcrumbs': generic.buildBreadcrumbs(currect_section), 
               'page_title': page_title, 
               'page_sections': sections, 
               'balances': balances, 
               'currency_symbols': currency_symbols,
               'currency_names': currency_names,
               'transactions': transactions,
               'events': list_of_events
               }
    return render(request, 'dashboard/index.html', context)

@login_required
@csrf_exempt
def proxy(request):
    '''
    Proxy script view for rates ticker APIs
    '''
    
    if request.is_ajax():
        if request.method == 'POST':
            url = request.body
            connector.cache.setDebug(True)
            cache_hash = connector.getParamHash(url)
            cache_object = connector.cache.fetch('rates', cache_hash)
            if cache_object:
                return HttpResponse(cache_object, content_type="application/json")
            else:
                opener = urllib2.build_opener()
                opener.addheaders = [('User-agent', "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:25.0) Gecko/20100101 Firefox/25.0")]
                response = opener.open(url)
                rates_json = response.read()
                connector.cache.store('rates', cache_hash, rates_json, 60)
                return HttpResponse(rates_json, content_type="application/json")
