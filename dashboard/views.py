from connections import connector
import config
import generic
import calendar
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.models import Events

@login_required
def index(request):
    '''
    Handler for the dashboard main page
    '''
    currect_section = 'dashboard'
    
    balances = connector.getbalance()
    transactions_by_currency = connector.listtransactions(limit=20, start=0)
    transactions = []
    for currency in transactions_by_currency:
        for transaction in transactions_by_currency[currency]:
            if transaction['category'] != 'move':
                transaction['currency'] = currency
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
            transaction['source_addresses'] = connector.getaddressesbyaccount(transaction['account'], transaction['currency'])
            transaction['destination_address'] = transaction['address']
            transaction['icon'] = 'glyphicon-circle-arrow-up'
        elif transaction['category'] == 'move':
            transaction['source_address'] = connector.getaddressesbyaccount(transaction['account'], transaction['currency'])
            transaction['destination_address'] = connector.getaddressesbyaccount(transaction['otheraccount'], transaction['currency'])
            if not transaction['account']:
                transaction['alternative_name'] = '(no name)'
            transaction['icon'] = 'glyphicon-circle-arrow-right'

    currency_symbols = generic.getCurrencySymbol('*')
    
    currency_names = {}
    for currency in connector.config:
        currency_names[currency] = connector.config[currency]['currency_name']
    
    # events
    events = Events.objects.all().order_by('-entered')[:10]  
    for event in events:
        timestamp = calendar.timegm(event.entered.timetuple())
        event.entered_pretty = generic.twitterizeDate(timestamp)
    
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
               'events': events
               }
    return render(request, 'dashboard/index.html', context)
