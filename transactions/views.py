import math
import config
import generic
from connections import connector
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from addressbook.models import savedAddress
from django.contrib.auth.models import User

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
    
    # add a list of pages in the view
    sections = generic.getSiteSections(current_section)
    
    sender_address_tooltip_text = "This address has been calculated using the Input Script Signature. You should verify before using it."
    
    context = {
               'globals': config.MainConfig['globals'],
               'system_errors': connector.errors,
               'request': request,
               'breadcrumbs': generic.buildBreadcrumbs(current_section, '', current_activesession), 
               'page_title': page_title, 
               'page_sections': sections, 
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
