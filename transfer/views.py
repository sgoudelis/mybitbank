from connections import connector
from globals import globals
from lib import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import forms

def index(request):
    '''
    handler for the transfers
    '''
    page_title = "Transfer"
    
    # add a list of pages in the view
    globals['sections'] = getSiteSections('transfer')
    
    # get a list of source accounts
    accounts = connector.listaccounts()
    
    context = {'globals': globals, 'page_title': page_title, 'accounts': accounts}
    return render(request, 'transfer/index.html', context)

def send(request):
    '''
    handler for the transfers
    '''
    if request.method == 'POST': # If the form has been submitted...
        form = forms.SendCurrencyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = forms.SendCurrencyForm() # An unbound form
    
    page_title = "Transfer"
    
    # get a list of source accounts
    accounts = connector.listaccounts()
    context = {'globals': globals, 'page_title': page_title, 'accounts': accounts, 'form': form}
    return render(request, 'transfer/index.html', context)
    