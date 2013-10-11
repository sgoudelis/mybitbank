from connections import connector
from globals import globals
from lib import *
from django.http import HttpResponse
from django.shortcuts import render

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
    try:
        account_name = request.POST['account_name']
        currency = request.POST['currency']
        if not account_name:
            raise Exception('Account name not provided')
    except (Exception, KeyError) as e:
        context = getAddAccountFormContext(account_name=account_name, currency=currency, error=e)
        return render(request, 'accounts/add.html', context)
    else:
        # all ok, create account
        new_address = connector.getnewaddress(currency, account_name)
        return HttpResponseRedirect(reverse('accounts:index'))
    