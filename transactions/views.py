import math
import config
import generic
import datetime
from connections import connector
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from addressbook.models import savedAddress

current_section = 'transactions'

@login_required
def index(request, page=0):
    '''
    handler for the transactions
    '''
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
    transactions_list = generic.getTransactions(connector = connector, sort_by = 'time', reverse_order = True)
    
    # remove moves if there is a user setting for it
    transactions = []
    if hide_moves:
        for transaction in transactions_list:
            if transaction['category'] != "move":
                transactions.append(transaction)
    else:
        transactions = transactions_list
    
    for transaction in transactions:
        if transaction['category'] == "move" and hide_moves:
            continue
        
        transaction['currency_symbol'] = generic.getCurrencySymbol(transaction['currency'].lower())
        
        if transaction.get('confirmations', False) is not False:
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
            transaction['destination_address'] = transaction['address']
            transaction['icon'] = 'glyphicon-circle-arrow-down'
        elif transaction['category'] == 'send':
            if not len(transaction['account']):
                transaction['alternative_account'] = "(no name)"
            transaction['source_addresses'] = connector.getaddressesbyaccount(transaction['account'], transaction['currency'])
            transaction['destination_address'] = transaction['address']
            transaction['icon'] = 'glyphicon-circle-arrow-up'
            transaction['addressbook_name'] = saved_addresses.get(transaction['address'], False)
        elif transaction['category'] == 'move':
            transaction['source_addresses'] = connector.getaddressesbyaccount(transaction['account'], transaction['currency'])
            transaction['destination_addresses'] = connector.getaddressesbyaccount(transaction['otheraccount'], transaction['currency'])
            if not transaction['account']:
                transaction['alternative_name'] = '(no name)'
            transaction['icon'] = 'glyphicon-circle-arrow-right'
    
    # pagify
    if page is 0:
        # pager off
        selected_transactions = transactions
        max_page = 0
        pages = []
        show_pager = False
        current_activesession = ''
    else:
        # pager on
        page_id = page-1
        selected_transactions = transactions[(page_id*items_per_page):((page_id*items_per_page)+items_per_page)]
        max_page = int(math.ceil(len(transactions)/items_per_page))+1
        pages = [i+1 for i in range(max_page)]
        show_pager = True
        current_activesession = 'Page %s' % page
    
    sender_address_tooltip_text = "This address has been calculated using the Input Script Signature. You should verify before using it."
    
    context = {
               'globals': config.MainConfig['globals'],
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'request': request,
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', current_activesession), 
               'page_title': page_title, 
               'page_sections': generic.getSiteSections(current_section), 
               'transactions': selected_transactions, 
               'show_pager': show_pager, 
               'next_page': min((page+1), len(pages)), 
               'prev_page': max(1, page-1), 
               'pages': pages, 
               'current_page': page,
               'saved_addresses': saved_addresses,
               'sender_address_tooltip_text': sender_address_tooltip_text,
               }
    return render(request, 'transactions/index.html', context)

@login_required
def transactionDetails(request, txid, currency):
    
    transaction = connector.gettransaction(txid, currency)
    
    transaction['timereceived_pretty'] = generic.twitterizeDate(transaction.get('timereceived', 'never'))
    transaction['time_pretty'] = generic.twitterizeDate(transaction.get('time', 'never'))
    transaction['timereceived_human'] = datetime.datetime.fromtimestamp(transaction.get('timereceived', 0))
    transaction['time_human'] = datetime.datetime.fromtimestamp(transaction.get('time', 0))
    transaction['blocktime_human'] = datetime.datetime.fromtimestamp(transaction.get('blocktime', 0))
    transaction['blocktime_pretty'] = generic.twitterizeDate(transaction.get('blocktime', 'never'))
    transaction['currency'] = currency
    
    if transaction.get('fee', False):
        transaction['fee'] = generic.longNumber(transaction['fee'])
    else:
        transaction['fee'] = ""
        
    if transaction['details'][0]['category'] == 'receive':
        account = connector.getaccountdetailsbyaddress(transaction['details'][0]['address'])
    elif transaction['details'][0]['category'] == 'send':
        account_addresses = connector.getaddressesbyaccount(transaction['details'][0]['account'], currency)
        account = connector.getaccountdetailsbyaddress(account_addresses[0])
        
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