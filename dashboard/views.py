from connections import connector
from globals import globals
from lib import *
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    '''
    Handler for the dashboard
    '''
    
    balances = connector.getbalance()
    currency_symbols = getCurrencySymbol('*')
    
    page_title = "Dashboard"
    globals['sections'] = getSiteSections('dashboard')
    globals['connector_errors'] = connector.errors
    context = {'globals': globals, 'page_title': page_title, 'balances': balances, 'currency_symbols': currency_symbols}
    return render(request, 'dashboard/index.html', context)
