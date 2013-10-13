# -*- coding: UTF8 -*-
import datetime
import connections

def longNumber(x):
    '''
    Convert number coming from the JSON-RPC to a human readable format with 8 decimal
    '''
    return "{:.8f}".format(x)

def twitterizeDate(ts):
    '''
    Make a timestamp prettier
    '''
    
    if type(ts) is str:
        return ts
    
    mydate = datetime.datetime.fromtimestamp(ts)
    difference = datetime.datetime.now() - mydate
    s = difference.seconds
    if difference.days > 7 or difference.days < 0:
        return mydate.strftime('%d %b %y')
    elif difference.days == 1:
        return '1 day ago'
    elif difference.days > 1:
        return '{} days ago'.format(difference.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(s/60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(s/3600)


def getAllAccounts(connector):
    '''
    Return all accounts
    '''
    accounts = []
    accounts_by_name = connector.listaccounts()
    for currency in accounts_by_name.keys():
        for account in accounts_by_name[currency]:
            address = connector.getaddressesbyaccount(account['name'], currency)
            account['address'] = address
            account['currency'] = currency
            account['currency_symbol'] = getCurrencySymbol(currency)
            accounts.append(account)

    return accounts

def getAccountsWithNames(connector):
    '''
    Return accounts that have names only
    '''
    a = getAllAccounts(connector)
    accounts_with_names = []
    for acc in a:
        if acc['name']:
            accounts_with_names.append(acc);
            
    return accounts_with_names
    
def getTransactions(connector, account_name = None, sort_by = 'timereceived', reverse_order = False):
    '''
    Return transactions by account name
    '''
    transactions_ordered = []
    transactions = connector.listtransactions(account_name)
    for currency in transactions.keys():
        for transaction in transactions[currency]:
            transaction['currency'] = currency.upper()
            transaction['timereceived_pretty'] = twitterizeDate(transaction.get('timereceived', 'never'))
            transaction['time_pretty'] = twitterizeDate(transaction.get('time', 'never'))
            transaction['timereceived_human'] = datetime.datetime.fromtimestamp(transaction.get('timereceived', 0))
            transaction['time_human'] = datetime.datetime.fromtimestamp(transaction.get('time', 0))
            transactions_ordered.append(transaction)
    
    transactions_ordered = sorted(transactions_ordered, key=lambda k: k.get(sort_by,0), reverse=reverse_order)
    return transactions_ordered

def getSiteSections(active): 
    sections = [
                    {'name': 'dashboard', 'path':"/dashboard", 'title': 'Dashboard'},
                    {'name': 'accounts', 'path':"/accounts", 'title': 'Accounts'},
                    {'name': 'transactions', 'path':"/transactions/1", 'title': "Transactions"},
                    {'name': 'transfer', 'path':"/transfer", 'title': "Transfer"},
                    {'name': 'addressbook', 'path':"/addressbook", 'title': "Addressbook"},
               ]
    
    for section in sections:
        if section['name'] == active:
            section['active'] = True
    return sections

def getCurrencySymbol(for_currency='*'):
    currencies = {}
    connection_config = connections.connector.config
    for currency in connection_config.keys():
        currencies[currency] = connections.connector.config[currency]['symbol']
    
    if for_currency == '*':
        return currencies
    else:
        return currencies[for_currency]

