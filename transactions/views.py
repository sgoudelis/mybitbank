import config
import generic
import datetime
from connections import connector
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from addressbook.models import savedAddress

current_section = 'transactions'

@login_required
def index(request, selected_provider_id=False, page=1):
    '''
    handler for the transactions list
    '''
    
    if selected_provider_id is False:
        selected_provider_id = connector.config.keys()[0]
    else:
        selected_provider_id = int(selected_provider_id)
        
    page = int(page)
    items_per_page = 10
    page_title = "Transactions"
    
    hide_moves = request.user.setting.get('hide_moves')
    
    # get addressbook
    addressBookAddresses = savedAddress.objects.filter(status__gt=1)
    saved_addresses = {}
    for saved_address in addressBookAddresses:
        saved_addresses[saved_address.address] = saved_address.name

    # get transactions
    transactions_list = connector.listtransactionsbyaccount('*', selected_provider_id, items_per_page, (items_per_page*(page-1)))
    # sort transactions
    transactions_list = sorted(transactions_list, key=lambda k: k.get('time',0), reverse=True)
    
    # remove moves if there is a user setting for it
    transactions = []
    if bool(hide_moves):
        for transaction in transactions_list:
            if transaction['category'] != "move":
                transactions.append(transaction)
    else:
        transactions = transactions_list
    
    for transaction in transactions:
        if transaction['category'] == "move" and hide_moves:
            continue
        
        transaction['currency_symbol'] = generic.getCurrencySymbol(transaction['currency'].lower())
        
        if transaction.get('category', False) in ['receive','send']:
            if transaction['confirmations'] <= config.MainConfig['globals']['confirmation_limit']:
                transaction['status_icon'] = 'glyphicon-time'
                transaction['status_color'] = '#AAA';
                transaction['tooltip'] = transaction['confirmations']
            else:
                transaction['status_icon'] = 'glyphicon-ok-circle'
                transaction['status_color'] = '#1C9E3F';
                transaction['tooltip'] = transaction['confirmations']
        
        if transaction['category'] == 'receive':
            transaction['source_address'] = transaction.get('details', {}).get('sender_address', '(no sender address)')
            transaction['addressbook_name'] = saved_addresses.get(transaction['source_address'], False)
            transaction['icon'] = 'glyphicon-circle-arrow-down'
            if not len(transaction['account']):
                transaction['account'] = "(default account)"
                default_account = connector.getdefaultaccount(transaction['provider_id'])
                transaction['destination_address'] = default_account['addresses'][0]
            else:
                transaction['destination_address'] = transaction['address']
                
        elif transaction['category'] == 'send':
            transaction['source_addresses'] = connector.getaddressesbyaccount(transaction['account'], transaction['provider_id'])
            transaction['destination_address'] = transaction['address']
            transaction['icon'] = 'glyphicon-circle-arrow-up'
            transaction['addressbook_name'] = saved_addresses.get(transaction['address'], False)
            if not len(transaction['account']):
                transaction['account'] = "(default account)"
                default_account = connector.getdefaultaccount(transaction['provider_id'])
                transaction['destination_address'] = default_account['addresses'][0]
            else:
                transaction['destination_address'] = transaction['address']
            
        elif transaction['category'] == 'move':
            transaction['source_addresses'] = connector.getaddressesbyaccount(transaction['account'], transaction['provider_id'])
            transaction['destination_addresses'] = connector.getaddressesbyaccount(transaction['otheraccount'], transaction['provider_id'])
            transaction['icon'] = 'glyphicon-circle-arrow-right'
            if not len(transaction['account']):
                transaction['account'] = "(default account)"
                default_account = connector.getdefaultaccount(transaction['provider_id'])
                transaction['destination_address'] = default_account['addresses'][0]
            if not len(transaction['otheraccount']):
                transaction['otheraccount'] = "(default account)"
                default_account = connector.getdefaultaccount(transaction['provider_id'])
                transaction['source_addresses'] = default_account['addresses']
            
    sender_address_tooltip_text = "This address has been calculated using the Input Script Signature. You should verify before using it."
    
    providers = {}
    for provider_id in connector.config:
        providers[provider_id] = connector.config[provider_id]['name']
    
    context = {
               'globals': config.MainConfig['globals'],
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'request': request,
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', connector.config[selected_provider_id]['name']), 
               'page_title': page_title, 
               'page_sections': generic.getSiteSections(current_section), 
               'transactions': transactions, 
               'transactions_per_page': items_per_page,
               'show_pager': True, 
               'next_page': (page+1), 
               'prev_page': max(1, page-1), 
               'levels': [(max(1, (page-10)), max(1, (page-100)), max(1, (page-1000))), ((page+10), (page+100), (page+1000))],
               'current_page': page,
               'saved_addresses': saved_addresses,
               'sender_address_tooltip_text': sender_address_tooltip_text,
               'providers': providers,
               'selected_provider_id': selected_provider_id,
               }
    return render(request, 'transactions/index.html', context)

@login_required
def transactionDetails(request, txid, provider_id):
    provider_id = int(provider_id)
    transaction = connector.gettransaction(txid, provider_id)
    
    transaction['timereceived_pretty'] = generic.twitterizeDate(transaction.get('timereceived', 'never'))
    transaction['time_pretty'] = generic.twitterizeDate(transaction.get('time', 'never'))
    transaction['timereceived_human'] = datetime.datetime.fromtimestamp(transaction.get('timereceived', 0))
    transaction['time_human'] = datetime.datetime.fromtimestamp(transaction.get('time', 0))
    transaction['blocktime_human'] = datetime.datetime.fromtimestamp(transaction.get('blocktime', 0))
    transaction['blocktime_pretty'] = generic.twitterizeDate(transaction.get('blocktime', 'never'))
    transaction['currency'] = connector.config[provider_id]['currency']
    transaction['currency_symbol'] = generic.getCurrencySymbol(transaction['currency'])
    
    if transaction.get('fee', False):
        transaction['fee'] = generic.longNumber(transaction['fee'])
    else:
        transaction['fee'] = ""
        
    account_addresses = []
    if transaction['details'][0]['category'] == 'receive':
        if not len(transaction['details'][0]['account']):
            # get the default account for provider_id
            account = connector.getdefaultaccount(provider_id)
        else:
            account = connector.getaccountdetailsbyaddress(transaction['details'][0]['address'])
    elif transaction['details'][0]['category'] == 'send':
        account_addresses = connector.getaddressesbyaccount(transaction['details'][0]['account'], provider_id)
        account = connector.getaccountdetailsbyaddress(account_addresses[0])
        
    if not len(transaction['details'][0]['account']):
        transaction['details'][0]['account'] = '(default account)'
    
    page_title = "Transaction details for %s" % txid
    context = {
           'globals': config.MainConfig['globals'],
           'system_errors': connector.errors,
           'system_alerts': connector.alerts,
           'request': request,
           'breadcrumbs': generic.buildBreadcrumbs(current_section, '', 'Details of %s' % txid), 
           'page_title': page_title, 
           'page_sections': generic.getSiteSections(current_section), 
           'transaction': transaction,
           'account': account,
           'conf_limit': config.MainConfig['globals']['confirmation_limit'],
           }
    
    if request.method == 'GET':
        return render(request, 'transactions/details.html', context)
    else:
        # maybe convert to PDF ?
        return render(request, 'transactions/details.html', context)