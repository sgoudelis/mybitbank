import forms
import config
import generic
from connections import connector
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from addressbook.models import savedAddress
from django.contrib import messages

current_section = 'transfer'

@login_required
def index(request, selected_currency='btc'):
    '''
    handler for the transfers
    '''
    context = commonContext(request=request, selected_currency=selected_currency)
    context['request'] = request
    return render(request, 'transfer/index.html', context)

def commonContext(request={}, selected_currency='btc', form=None, errors=[], show_passphrase=False, show_warning_ssl=False):
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
    
    # addressbook values
    saved_addresses = savedAddress.objects.filter(currency=selected_currency, status__gt=1)
    addressbook_addresses = {}
    for saved_address in saved_addresses:
        addressbook_addresses[saved_address.address] = saved_address.name
    
    context = {
               'globals': config.MainConfig['globals'], 
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'request': request,
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
               'show_passphrase': show_passphrase,
               'ssl_warning': show_warning_ssl,
               'addressbook_addresses': addressbook_addresses
               }
    
    return context

@login_required
def send(request, currency):
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
            passphrase = form.cleaned_data['passphrase']
            
            # main exit flags
            move_exit = False
            sendfrom_exit = False
            
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
                    context = commonContext(request=request, selected_currency=selected_currency, form=form, errors=post_errors)
                    return render(request, 'transfer/index.html', context)
                
            else:
                
                if passphrase:
                    # a passphrase was given, unlock wallet first
                    unlock_exit = connector.walletpassphrase(passphrase, currency)
                    
                    if unlock_exit is not True:
                        # show form with error
                        post_errors.append({'message': unlock_exit['message']})
                        context = commonContext(request=request, selected_currency=selected_currency, form=form, errors=post_errors, show_passphrase=True)
                        return render(request, 'transfer/index.html', context)
                
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
                if type(sendfrom_exit) is dict and sendfrom_exit['code'] < 0:
                    
                    # check if passphrase is needed
                    if sendfrom_exit['code'] == -13:
                        # passphrase is needed
                        show_passphrase=True
                    else:
                        show_passphrase=False
                    
                    if not request.is_secure() and passphrase:
                        show_warning_ssl = True
                    else:
                        show_warning_ssl = False
                    
                    # show form with error
                    post_errors.append({'message': sendfrom_exit['message']})
                    context = commonContext(request=request, selected_currency=selected_currency, form=form, errors=post_errors, show_passphrase=show_passphrase, show_warning_ssl=show_warning_ssl)
                    return render(request, 'transfer/index.html', context)
                
            if passphrase:
                # lock wallet again
                connector.walletlock(currency)
                
            # process the data in form.cleaned_data
            if move_exit:
                messages.success(request, 'Local move of %s %s completed from account "%s" to "%s"' % (amount, currency.upper(), from_account['name'], to_account['name']), extra_tags="success")
            elif sendfrom_exit:
                messages.success(request, 'Transfer of %s %s initialized with transaction id %s' % (amount, currency.upper(), sendfrom_exit), extra_tags="success")
            return HttpResponseRedirect('/transactions/') # Redirect after POST
    else:
        form = forms.SendCurrencyForm()
        
    context = commonContext(request=request, selected_currency=currency, form=form)
    
    return render(request, 'transfer/index.html', context)
