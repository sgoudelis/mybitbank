from connections import connector
import config
import generic
from django.shortcuts import render

def index(request):
    '''
    Handler for the dashboard
    '''
    currect_section = 'dashboard'
    
    balances = connector.getbalance()
    currency_symbols = generic.getCurrencySymbol('*')
    page_title = "Dashboard"
    sections = generic.getSiteSections('dashboard')
    context = {'globals': config.MainConfig['globals'], 'breadcrumbs': generic.buildBreadcrumbs(currect_section), 'page_title': page_title, 'page_sections': sections, 'balances': balances, 'currency_symbols': currency_symbols}
    return render(request, 'dashboard/index.html', context)
