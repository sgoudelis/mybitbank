from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from mybitbank.apps.addressbook.models import savedAddress
from mybitbank.libs import misc
from mybitbank.libs.config import MainConfig
from mybitbank.libs.connections import connector
from mybitbank.libs.entities import getWallets, getWalletByProviderId


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

    # set the request in the connector object
    connector.request = request

    wallet = None
    wallets = getWallets(connector)
    for w in wallets:
        if w.provider_id == selected_provider_id:
            wallet = w
            
    # get transactions
    transactions_list = wallet.listTransactions(items_per_page, (items_per_page * (page - 1)))
    # sort transactions
    transactions_list = sorted(transactions_list, key=lambda k: k.get('time', 0), reverse=True)
    
    # remove moves if there is a user setting for it
    transactions = []
    if bool(hide_moves):
        for transaction in transactions_list:
            if transaction['category'] != "move":
                transactions.append(transaction)
    else:
        transactions = transactions_list

    sender_address_tooltip_text = "This address has been calculated using the Input Script Signature. You should verify before using it."
    
    providers = {}
    for provider_id in connector.config:
        providers[provider_id] = connector.config[provider_id]['name']
    
    context = {
               'globals': MainConfig['globals'],
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'request': request,
               'breadcrumbs': misc.buildBreadcrumbs(current_section, '', connector.config[selected_provider_id]['name']),
               'page_title': page_title,
               'page_sections': misc.getSiteSections(current_section),
               'transactions': transactions,
               'transactions_per_page': items_per_page,
               'show_pager': True,
               'next_page': (page + 1),
               'prev_page': max(1, page - 1),
               'levels': [(max(1, (page - 10)), max(1, (page - 100)), max(1, (page - 1000))), ((page + 10), (page + 100), (page + 1000))],
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
    
    # set the request in the connector object
    connector.request = request
    
    # get wallet for provider_id
    wallet = getWalletByProviderId(connector, provider_id) 
    
    transaction = wallet.getTransactionById(txid)
    
    if transaction.get('fee', False):
        transaction['fee'] = misc.longNumber(transaction['fee'])
    else:
        transaction['fee'] = ""
        
    if transaction['details'][0]['category'] == 'receive':
        if not len(transaction['details'][0]['account']):
            # get the default account for provider_id
            account = wallet.getDefaultAccount()
        else:
            account = wallet.getAccountByAddress(transaction['details'][0]['address'])
    elif transaction['details'][0]['category'] == 'send':
        account = transaction['account']
    
    page_title = "Transaction details for %s" % txid
    context = {
           'globals': MainConfig['globals'],
           'system_errors': connector.errors,
           'system_alerts': connector.alerts,
           'request': request,
           'breadcrumbs': misc.buildBreadcrumbs(current_section, '', 'Details of %s' % txid),
           'page_title': page_title,
           'page_sections': misc.getSiteSections(current_section),
           'transaction': transaction,
           'account': account,
           'conf_limit': MainConfig['globals']['confirmation_limit'],
           }
    
    if request.method == 'GET':
        return render(request, 'transactions/details.html', context)
    else:
        # maybe convert to PDF ?
        return render(request, 'transactions/details.html', context)
