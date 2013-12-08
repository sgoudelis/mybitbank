import config
import forms
import generic
import datetime
import events
from connections import connector
from accounts.models import addressAliases
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from addressbook.models import savedAddress
from django.utils import simplejson
from django.contrib import messages
from django.utils.timezone import utc

current_section = 'accounts'

@login_required
def index(request):
    '''
    Handler for the accounts view
    '''
    sections = generic.getSiteSections(current_section)
    accounts = generic.getAllAccounts(connector)
    #transactions = generic.getTransactions(connector = connector, reverse_order = True)
    transactions = []
    
    # find the last transaction for each account
    for account in accounts:
        transactions = connector.listtransactionsbyaccount(account['name'], account['provider_id'], 1, 0)
        for transaction in transactions:
            if account['name'] == transaction['account']:
                account['last_activity'] = generic.twitterizeDate(transaction['time'])
                account['address_count'] = len(account['addresses']) - 1
                break
        else:
            account['last_activity'] = "never"
    
    page_title = _("Accounts")
    context = {
               'globals': config.MainConfig['globals'], 
               'breadcrumbs': generic.buildBreadcrumbs(current_section, 'all'), 
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'page_title': page_title, 
               'page_sections': sections, 
               'accounts': accounts,
               'request': request,
               }
    return render(request, 'accounts/index.html', context)

@login_required
def add(request):
    '''
    Handler for the account create form
    '''
    form = forms.CreateAccountForm()
    context = getAddAccountFormContext(form=form)
    context['breadcrumbs'] = generic.buildBreadcrumbs(current_section, '', 'Create')
    return render(request, 'accounts/add.html', context)

def getAddAccountFormContext(account_name='', error=None, form=None):
    '''
    Provide a common context between the account view and create account view
    '''
    # get available currencies
    providers_available = []
    providers = connector.config.keys()
    for provider_id in providers:
        providers_available.append({'id': provider_id, 'currency': connector.config[provider_id]['currency'], 'name': connector.config[provider_id]['name']})
        
    page_title = _("Create account")
    sections = generic.getSiteSections(current_section)
    context = {
               'globals': config.MainConfig['globals'], 
               'system_alerts': connector.alerts,
               'system_errors': connector.errors,
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', 'Create'),
               'page_sections': sections, 
               'page_title': page_title, 
               'providers': providers_available, 
               'account_name': account_name, 
               'provider_id': provider_id, 
               'error_message': error,
               'form': form,
               }
    return context

@login_required
def create(request):
    '''
    Handler for POST of create account form
    '''
    
    if request.method == 'POST': 
        
        # we have a POST request
        form = forms.CreateAccountForm(request.POST)

        if form.is_valid(): 
            new_account_name = form.cleaned_data['account_name']
            provider_id = form.cleaned_data['provider_id']
            
            # all ok, create account
            new_address = connector.getnewaddress(provider_id, new_account_name)
            
            if new_address:
                messages.success(request, 'New account created with one address (%s)' % new_address, extra_tags="success")
                events.addEvent(request, 'Created new account with address "%s"' % (new_address), 'info')
                
            return HttpResponseRedirect(reverse('accounts:index'))

    else:
        form = forms.CreateAccountForm()
    
    context = getAddAccountFormContext(account_name="", form=form)
    return render(request, 'accounts/add.html', context)
    
@login_required        
def details(request, account_address="pipes", page=1):
    '''
    Handler for the account details
    '''
    transactions_per_page = 10
    page = int(page)
    
    # add a list of pages in the view
    sections = generic.getSiteSections(current_section)
    
    # get account details
    account = connector.getaccountdetailsbyaddress(account_address)
    currency_symbol = generic.getCurrencySymbol(account['currency'])
    currency_name = connector.config[account['provider_id']]['name']
    
    # get addressbook
    addressBookAddresses = savedAddress.objects.filter(status__gt=1)
    saved_addresses = {}
    for saved_address in addressBookAddresses:
        saved_addresses[saved_address.address] = saved_address.name
    
    if account:
        # get transaction details
        transactions = generic.getTransactionsByAccount(connector, account['name'], account['provider_id'], reverse_order=True, count=transactions_per_page, start=(transactions_per_page*(page-1)))
        for transaction in transactions:
            transaction['currency_symbol'] = generic.getCurrencySymbol(transaction['currency'].lower())
            if not transaction.get('details', {}).get('sender_address', False):
                    transaction['details']['sender_address'] = '(unknown)'
            
            # addressbook names and address resolution
            if transaction['category'] == 'move':
                transaction['otheraccount_address'] = connector.getaddressesbyaccount(transaction['otheraccount'], transaction['currency'])
            elif transaction['category'] == 'receive':
                transaction['source_address'] = transaction.get('details', {}).get('sender_address', '(no sender address)')
                transaction['addressbook_name'] = saved_addresses.get(transaction['source_address'], False)
            elif transaction['category'] == 'send':
                transaction['source_addresses'] = connector.getaddressesbyaccount(transaction['account'], transaction['currency'])
                transaction['addressbook_name'] = saved_addresses.get(transaction['address'], False)
                
            # use icons and colors to represent confirmations
            if transaction.get('confirmations', False) is not False:
                if transaction['confirmations'] <= config.MainConfig['globals']['confirmation_limit']:
                    transaction['status_icon'] = 'glyphicon-time'
                    transaction['status_color'] = '#DDD';
                    transaction['tooltip'] = transaction['confirmations']
                else:
                    transaction['status_icon'] = 'glyphicon-ok-circle'
                    transaction['status_color'] = '#1C9E3F';
                    transaction['tooltip'] = transaction['confirmations']
    else:
        account = {}
        account['name'] = _('no such account')
        transactions = []
    
    page_title = _("Account details for %s") % (account['name'] or account['alternative_name'])
    sender_address_tooltip_text = "This address has been calculated using the Input Script Signature. You should verify before using it."
    
    context = {
               'globals': config.MainConfig['globals'],
               'request': request,
               'system_alerts': connector.alerts,
               'system_errors': connector.errors,
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', account['name'] or account['alternative_name']), 
               'page_title': page_title, 
               'current_page': page,
               'next_page': (page+1), 
               'prev_page': max(1, page-1), 
               'levels': [(max(1, (page-10)), max(1, (page-100)), max(1, (page-1000))), ((page+10), (page+100), (page+1000))],
               'page_sections': sections, 
               'account': account,
               'transactions': transactions,
               'currency_name': currency_name,
               'currency_symbol': currency_symbol,
               'account_address': account_address,
               'sender_address_tooltip_text': sender_address_tooltip_text,
               'transactions_per_page': transactions_per_page,
               }
    
    return render(request, 'accounts/details.html', context)
    
@login_required  
def setAddressAlias(request):
    '''
    Set address alias
    '''
    return_msg = {'alias': ''}
    
    if request.method == 'POST':
        form = forms.SetAddressAliasForm(request.POST)
        if form.is_valid():
            # form is valid
            alias = form.cleaned_data['alias']
            address = form.cleaned_data['address']
            
            # check if address already has an alias, if multiple aliases exist for the same address, ignore them for now
            address_alias = addressAliases.objects.filter(address=address, status__gt=1)
            if address_alias:
                address_alias[0].alias = alias
                address_alias[0].save()
                events.addEvent(request, 'Updated alias for address "%s" to %s' % (address, alias), 'info')
            else:
                events.addEvent(request, 'Added alias "%s" for address "%s"' % (alias, address), 'info')
                address_alias = addressAliases.objects.create(address=address, alias=alias, status=2, entered=datetime.datetime.utcnow().replace(tzinfo=utc))
            
            if address_alias:
                return_msg = {'alias': alias}
            else:
                return_msg = {'alias': 'sugnomi xasate'}
                
    json = simplejson.dumps(return_msg)             
    return HttpResponse(json, mimetype="application/x-javascript")

@login_required
def createNewAddress(request, old_address):
    '''
    Create a new address for the account of old_address
    '''
    if request.method == 'POST': 
        account_details = connector.getaccountdetailsbyaddress(old_address)
        if account_details:
            new_address = connector.getnewaddress(account_details['provider_id'], account_details['name'])
            messages.success(request, 'New address %s created' % new_address, extra_tags="success")
            events.addEvent(request, 'New address "%s" created for account "%s"' % (new_address, account_details['name']), 'info')
        return HttpResponseRedirect(reverse('accounts:details', kwargs={'account_address': old_address}))
    
    