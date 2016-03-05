"""
The MIT License (MIT)

Copyright (c) 2016 Stratos Goudelis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import forms

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from mybitbank.apps.addressbook.models import savedAddress
from mybitbank.libs import events, misc
from mybitbank.libs.config import MainConfig
from mybitbank.libs.connections import connector
from mybitbank.libs.entities import getWalletByProviderId


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
    
    # set the request in the connector object
    connector.request = request
    
    # get wallet for provider_id
    wallet = getWalletByProviderId(connector, selected_provider_id)
    
    # get all, codes, names and symbols for currencies
    currency_codes = {}
    currency_names = {}
    currency_symbols = {}
    for provider_id in connector.config:
        currency_names[provider_id] = connector.config[provider_id]['name']
        currency_symbols[provider_id] = connector.config[provider_id]['symbol']
        currency_codes[provider_id] = connector.config[provider_id]['currency']
            
    # sort in reverse
    # currency_codes = sorted(currency_codes)
    
    # get a list of source accounts
    accounts = wallet.listAccounts(gethidden=True, getarchived=True)
    
    # addressbook values
    saved_addresses = savedAddress.objects.filter(currency=currency_codes.get(selected_provider_id, None), status__gt=1)
    addressbook_addresses = {}
    for saved_address in saved_addresses:
        addressbook_addresses[saved_address.address] = saved_address.name

    context = {
               'globals': MainConfig['globals'],
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'request': request,
               'breadcrumbs': misc.buildBreadcrumbs(current_section, '', currency_names.get(selected_provider_id, "n/a")),
               'page_sections': misc.getSiteSections('transfer'),
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
    selected_provider_id = int(selected_provider_id)
    
    # set the request in the connector object
    connector.request = request
    
    if request.method == 'POST': 
        # we have a POST request
        form = forms.SendCurrencyForm(request.POST)
        
        if form.is_valid():
            # all validation rules pass
            from_account_identifier = form.cleaned_data['from_account']
            to_address = form.cleaned_data['to_address']
            to_account = form.cleaned_data['to_account']
            comment = form.cleaned_data['comment']
            comment_to = form.cleaned_data['comment_to']
            amount = form.cleaned_data['amount']
            provider_id = form.cleaned_data['provider_id']
            passphrase = form.cleaned_data['passphrase']
            
            # main exit flags
            move_exit = False
            sendfrom_exit = False
            
            # get from account details
            wallet = getWalletByProviderId(connector, selected_provider_id)
            list_of_accounts = wallet.listAccounts(gethidden=True, getarchived=True)
            from_account = None
            for account in list_of_accounts:
                if account['identifier'] == from_account_identifier:
                    from_account = account
                    break
            else:
                # account name not found, display error
                post_errors.append({'message': "The source account was not found!"})
                context = commonContext(request=request, selected_provider_id=provider_id, form=form, errors=post_errors)
                return render(request, 'transfer/index.html', context)
            
            # get to account details if there is one
            to_account = wallet.getAccountByAddress(to_address)
            # if to_account is set then it is a local move, do a move()
            if to_account:
                # this address/account is hosted locally, do a move
                move_exit = connector.moveAmount(
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
                # otherwise do a sendfrom(), it is a regular transaction
                if passphrase:
                    # a passphrase was given, unlock wallet first
                    unlock_exit = connector.walletPassphrase(passphrase, provider_id)
                    
                    if unlock_exit is not True:
                        # show form with error
                        post_errors.append({'message': unlock_exit['message']})
                        context = commonContext(request=request, selected_provider_id=provider_id, form=form, errors=post_errors, show_passphrase=True)
                        return render(request, 'transfer/index.html', context)
                
                # to_address not local, do a send
                sendfrom_exit = connector.sendFrom(
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
                        show_passphrase = True
                    else:
                        show_passphrase = False
                    
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
                connector.walletLock(provider_id)
                
            # process the data in form.cleaned_data
            if move_exit:
                messages.success(request, 'Local move of %s %s completed from account "%s" to "%s"' % (amount, connector.config[provider_id]['currency'].upper(), from_account['name'], to_account['name']), extra_tags="success")
                events.addEvent(request, 'Local move occurred from "%s" to "%s" in the amount of %s %s' % (from_account['name'], to_account['name'], amount, connector.config[provider_id]['currency'].upper()), 'info')
                return HttpResponseRedirect(reverse('transactions:index', kwargs={'selected_provider_id': selected_provider_id, 'page': '1'}))  # Redirect after POST
            elif sendfrom_exit:
                messages.success(request, 'Transfer of %s %s initialized with transaction id %s' % (amount, connector.config[provider_id]['currency'].upper(), sendfrom_exit), extra_tags="success")
                events.addEvent(request, 'Transfer initialized from "%s" to "%s" of %s %s' % (from_account['name'], to_address, amount, connector.config[provider_id]['currency'].upper()), 'info')
                return HttpResponseRedirect(reverse('transactions:details', kwargs={'provider_id': provider_id, 'txid':sendfrom_exit}))  # Redirect after POST
        
        else:
            # form not valid
            #messages.error(request, 'There were some errors processing this form!', extra_tags="error")
            print "Error processing form!"
            
    else:
        # request not a POST
        form = forms.SendCurrencyForm()
        
    context = commonContext(request=request, selected_provider_id=selected_provider_id, form=form)
    
    return render(request, 'transfer/index.html', context)
