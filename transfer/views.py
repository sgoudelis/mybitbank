from connections import connector
import config
import generic
from django.http import HttpResponseRedirect
from django.shortcuts import render
import forms
from django.core.urlresolvers import reverse

current_section = 'transfer'

def index(request, selected_currency='btc'):
    '''
    handler for the transfers
    '''
    context = commonContext(selected_currency)
    return render(request, 'transfer/index.html', context)

def commonContext(selected_currency='btc', form=None, errors=[]):
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
               'system_errors': connector.errors,
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', currency_names[selected_currency]), 
               'page_sections': generic.getSiteSections('transfer'), 
               'page_title': page_title,
               'currency_codes': currency_codes,
               'currency_names': currency_names,
               'currency_symbols': currency_symbols,
               'accounts': accounts,
               'selected_currency': selected_currency,
               'form': form,
               'errors': errors,
               }
    
    return context

def send(request):
    '''
    handler for the transfers
    '''
    post_errors = []
    
    if request.method == 'POST': 
        # we have a POST request
        form = forms.SendCurrencyForm(request.POST)
        
        if form.is_valid(): 
            # all validation rules pass
            from_address = form.cleaned_data['from_address']
            to_address = form.cleaned_data['to_address']
            comment = form.cleaned_data['comment']
            comment_to = form.cleaned_data['comment_to']
            amount = form.cleaned_data['amount']
            selected_currency = form.cleaned_data['selected_currency']

            # get account details
            from_account = connector.getaccountdetailsbyaddress(from_address)
            to_account = connector.getaccountdetailsbyaddress(to_address)
            if to_account:
                # this address/account is hosted locally, do a move
                move_exit = connector.moveamount(
                                                 from_account=from_account['name'], 
                                                 to_account=to_account['name'], 
                                                 currency=selected_currency, 
                                                 amount=amount, 
                                                 comment=comment
                                                )
                
                # if there are errors, show them in the UI
                if move_exit is not True:
                    post_errors.append({'message': move_exit['message']})
                    context = commonContext(selected_currency=selected_currency, form=form, errors=post_errors)
                    return render(request, 'transfer/index.html', context)
                
            else:
                # to_address not local, do a send
                sendfrom_exit = connector.sendfrom(
                                                   from_account=from_account['name'], 
                                                   to_address=to_address, 
                                                   amount=amount, 
                                                   currency=selected_currency, 
                                                   comment=comment, 
                                                   comment_to=comment_to
                                                  )

                # if there are errors, show them in the UI
                if sendfrom_exit['code'] < 0:
                    post_errors.append({'message': sendfrom_exit['message']})
                    context = commonContext(selected_currency=selected_currency, form=form, errors=post_errors)
                    return render(request, 'transfer/index.html', context)
                
            # process the data in form.cleaned_data
            return HttpResponseRedirect('/transactions/') # Redirect after POST
    else:
        form = forms.SendCurrencyForm()
        
    context = commonContext(form=form)
    
    return render(request, 'transfer/index.html', context)
