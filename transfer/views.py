import forms
import config
import generic
import events
from connections import connector
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from addressbook.models import savedAddress
from django.contrib import messages
from django.core.urlresolvers import reverse

current_section = 'transfer'

@login_required
def index(request, selected_provider_id=1):
    '''
    handler for the transfers
    '''
    selected_provider_id = int(selected_provider_id)
    
    context = commonContext(request=request, selected_provider_id=selected_provider_id)
    context['request'] = request
    return render(request, 'transfer/index.html', context)

def commonContext(request={}, selected_provider_id=1, form=None, errors=[], show_passphrase=False, show_warning_ssl=False):
    '''
    This constructs a common context between the two views: index and send
    '''
    page_title = "Transfer"
    selected_provider_id = int(selected_provider_id)
    
    currency_codes = {}
    currency_names = {}
    currency_symbols = {}
    for provider_id in connector.config:
        currency_names[provider_id] = connector.config[provider_id]['name']
        currency_symbols[provider_id] = connector.config[provider_id]['symbol']
        currency_codes[provider_id] = connector.config[provider_id]['currency']
            
    # sort in reverse
    #currency_codes = sorted(currency_codes)
    
    # get a list of source accounts
    accounts = connector.listaccounts(gethidden=True, getarchived=True)
    
    # adding currency symbol to accounts dictionary
    for currency in accounts.keys():
        for account in accounts[currency]:
            account['currency_symbol'] = currency_symbols[currency]
    
    # addressbook values
    saved_addresses = savedAddress.objects.filter(currency=currency_codes.get(selected_provider_id, None), status__gt=1)
    addressbook_addresses = {}
    for saved_address in saved_addresses:
        addressbook_addresses[saved_address.address] = saved_address.name
    
    context = {
               'globals': config.MainConfig['globals'], 
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'request': request,
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', currency_names.get(selected_provider_id, "n/a")), 
               'page_sections': generic.getSiteSections('transfer'), 
               'page_title': page_title,
               'currency_codes': currency_codes,
               'currency_names': currency_names,
               'currency_symbols': currency_symbols,
               'accounts': accounts,
               'selected_provider_id': selected_provider_id,
               'form': form,
               'errors': errors,
               'show_passphrase': show_passphrase,
               'ssl_warning': show_warning_ssl,
               'addressbook_addresses': addressbook_addresses
               }
    
    return context

@login_required
def send(request, selected_provider_id):
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
            provider_id = form.cleaned_data['provider_id']
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
                                                 provider_id=provider_id, 
                                                 amount=amount, 
                                                 comment=comment
                                                )
                
                # if there are errors, show them in the UI
                if move_exit is not True:
                    post_errors.append({'message': move_exit['message']})
                    context = commonContext(request=request, selected_provider_id=provider_id, form=form, errors=post_errors)
                    return render(request, 'transfer/index.html', context)
                
            else:
                
                if passphrase:
                    # a passphrase was given, unlock wallet first
                    unlock_exit = connector.walletpassphrase(passphrase, provider_id)
                    
                    if unlock_exit is not True:
                        # show form with error
                        post_errors.append({'message': unlock_exit['message']})
                        context = commonContext(request=request, selected_provider_id=provider_id, form=form, errors=post_errors, show_passphrase=True)
                        return render(request, 'transfer/index.html', context)
                
                # to_address not local, do a send
                sendfrom_exit = connector.sendfrom(
                                                   from_account=from_account['name'], 
                                                   to_address=to_address, 
                                                   amount=amount, 
                                                   provider_id=provider_id, 
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
                    
                    if not request.is_secure() and show_passphrase:
                        show_warning_ssl = 1
                    elif request.is_secure() and show_passphrase:
                        show_warning_ssl = -1
                    else:
                        show_warning_ssl = 0
                    
                    # show form with error
                    post_errors.append({'message': sendfrom_exit['message']})
                    context = commonContext(request=request, selected_provider_id=provider_id, form=form, errors=post_errors, show_passphrase=show_passphrase, show_warning_ssl=show_warning_ssl)
                    return render(request, 'transfer/index.html', context)
                
            if passphrase:
                # lock wallet again
                connector.walletlock(provider_id)
                
            # process the data in form.cleaned_data
            if move_exit:
                messages.success(request, 'Local move of %s %s completed from account "%s" to "%s"' % (amount, connector.config[provider_id]['currency'].upper(), from_account['name'], to_account['name']), extra_tags="success")
                events.addEvent(request, 'Local move occurred from "%s" to "%s" in the amount of %s %s' % (from_account['name'], to_account['name'], amount, connector.config[provider_id]['currency'].upper()), 'info')
                return HttpResponseRedirect(reverse('transactions:index', kwargs={'page': '1'})) # Redirect after POST
            elif sendfrom_exit:
                messages.success(request, 'Transfer of %s %s initialized with transaction id %s' % (amount, connector.config[provider_id]['currency'].upper(), sendfrom_exit), extra_tags="success")
                events.addEvent(request, 'Transfer initialized from "%s" to "%s" of %s %s' % (from_account['name'], to_address, amount, connector.config[provider_id]['currency'].upper()), 'info')
                return HttpResponseRedirect(reverse('transactions:details', kwargs={'provider_id': provider_id, 'txid':sendfrom_exit})) # Redirect after POST
            
    else:
        form = forms.SendCurrencyForm()
        
    context = commonContext(request=request, selected_provider_id=selected_provider_id, form=form)
    
    return render(request, 'transfer/index.html', context)
