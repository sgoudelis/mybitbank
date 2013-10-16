from connections import connector
from globals import globals
from lib import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import math
import pprint 

def index(request, page=0):
    '''
    handler for the transactions
    '''
    page = int(page)
    items_per_page = 10
    page_title = "Transactions"
    
    transactions = getTransactions(connector = connector, sort_by = 'time', reverse_order = True)
    
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(transactions)
    
    for transaction in transactions:
        transaction['currency_symbol'] = getCurrencySymbol(transaction['currency'].lower())
        if transaction['category'] == 'receive':
            transaction['icon'] = 'glyphicon-circle-arrow-down'
        elif transaction['category'] == 'send':
            transaction['icon'] = 'glyphicon-circle-arrow-up'
        elif transaction['category'] == 'move':
            transaction['icon'] = 'glyphicon-circle-arrow-right'
    
    # pagify
    if page is 0:
        # pager off
        selected_transactions = transactions
        max_page = 0
        pages = []
        show_pager = False
    else:
        # pager on
        page_id = page-1
        selected_transactions = transactions[(page_id*items_per_page):((page_id*items_per_page)+items_per_page)]
        max_page = int(math.ceil(len(transactions)/items_per_page))+1
        pages = [i+1 for i in range(max_page)]
        show_pager = True
    
    # add a list of pages in the view
    globals['sections'] = getSiteSections('transactions')
    globals['connector_errors'] = connector.errors
    context = {'globals': globals, 'page_title': page_title, 'transactions': selected_transactions, 'show_pager': show_pager, 'next_page': min((page+1), len(pages)), 'prev_page': max(1, page-1), 'pages': pages, 'current_page': page}
    return render(request, 'transactions/index.html', context)

