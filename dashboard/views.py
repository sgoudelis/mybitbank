from connections import connector
from globals import globals
from lib import *
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    '''
    URLconf handler for the dashboard
    '''
    page_title = "Dashboard"
    

    
    accounts = getAccountsWithNames(connector)
    transactions = getTransactions(connector = connector, reverse_order = True)
    
    # find the first transaction for each account
    last_activity = {}
    for account in accounts:
        for transaction in transactions:
            if account['name'] == transaction['account']:
                account['last_activity'] = twitterizeDate(transaction['time'])
                break
    
    # add a list of pages in the view
    globals['sections'] = getSiteSections('dashboard')
    globals['connector_errors'] = connector.errors
    context = {'globals': globals, 'page_title': page_title, 'accounts': accounts, 'transactions': transactions}
    return render(request, 'dashboard/index.html', context)
