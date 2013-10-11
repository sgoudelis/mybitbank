from connections import connector
from globals import globals
from lib import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

def index(request):
    '''
    handler for the transactions
    '''
    page_title = "Transactions"
    
    transactions = getTransactions(connector = connector, sort_by = 'timereceived', reverse_order = True)
    print transactions
    for transaction in transactions:
        if transaction['category'] == 'receive':
            transaction['icon'] = 'glyphicon-circle-arrow-down'
        elif transaction['category'] == 'send':
            transaction['icon'] = 'glyphicon-circle-arrow-up'
    
    # add a list of pages in the view
    globals['sections'] = getSiteSections('transactions')
    globals['connector_errors'] = connector.errors
    context = {'globals': globals, 'page_title': page_title, 'transactions': transactions}
    return render(request, 'transactions/index.html', context)