from connections import connector
import config
import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render
import forms
from django.core.urlresolvers import reverse
from django.forms.forms import Form
from lxml.html.builder import FORM

current_section = 'transfer'

def index(request, selected_currency='btc'):
    '''
    handler for the transfers
    '''
    context = commonContext(selected_currency)
    return render(request, 'transfer/index.html', context)

def commonContext(selected_currency='btc', form=None):
    '''
    This constructs a common context between the two views: index and send
    '''
    page_title = "Transfer"
    
    currency_codes = []
    currency_names = {}
    currency_symbols = {}
    for currency in connector.config:
        currency_names[currency] = connector.config[currency]['currency_name']
        currency_symbols[currency] = connector.config[currency]['symbol']
        currency_codes.append(currency)
    
    # sort in reverse
    currency_codes = sorted(currency_codes)
    
    # get a list of source accounts
    accounts = connector.listaccounts()
    
    # adding currency symbol to accounts dictionary
    for currency in accounts.keys():
        for account in accounts[currency]:
            account['currency_symbol'] = currency_symbols[currency]
    
    context = {
               'globals': config.MainConfig['globals'], 
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', currency_names[selected_currency]), 
               'page_sections': generic.getSiteSections('transfer'), 
               'page_title': page_title,
               'currency_codes': currency_codes,
               'currency_names': currency_names,
               'currency_symbols': currency_symbols,
               'accounts': accounts,
               'selected_currency': selected_currency,
               'form': form,
               }
    
    return context

def send(request):
    '''
    handler for the transfers
    '''
    if request.method == 'POST': 
        # we have a POST request
        form = forms.SendCurrencyForm(request.POST)
        
        if form.is_valid(): # All validation rules pass
            
            
            
            
            
            # process the data in form.cleaned_data
            return HttpResponseRedirect('/transfer/') # Redirect after POST
    else:
        form = forms.SendCurrencyForm() # An unbound form
        
    context = commonContext(form=form)
    
    return render(request, 'transfer/index.html', context)
