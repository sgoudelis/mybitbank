# -*- coding: utf-8 -*-
import datetime
import dateutil.relativedelta
import connections
import config
from django.utils.timezone import utc

def longNumber(x):
    '''
    Convert number coming from the JSON-RPC to a human readable format with 8 decimal
    '''
    return "{:.8f}".format(x)

def twitterizeDate(ts):
    '''
    Make a timestamp prettier eg. 1 hour ago
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

def timeSince(time):
    '''
    Humanized time format eg. 1h 23m 23s
    '''
    dt = datetime.datetime.fromtimestamp(time)
    rd = dateutil.relativedelta.relativedelta (datetime.datetime.now(), dt)
    s = ""
    if(rd.years > 0):
        s += "%dy " % (rd.years)
    if(rd.months > 0):
        s += "%dm " % (rd.months)
    if(rd.days > 0):
        s += "%dd " % (rd.days)
    if(rd.hours > 0):
        s += "%dh " % (rd.hours)
    if(rd.minutes > 0):
        s += "%dm " % (rd.minutes)
    if(rd.seconds > 0):
        s += "%ds" % (rd.seconds)
    return s    

def getAllAccounts(connector):
    '''
    Return all accounts
    '''
    accounts = []
    accounts_by_name = connector.listaccounts()
    for provider_id in accounts_by_name.keys():
        for account in accounts_by_name[provider_id]:
            account['currency'] = connector.config[provider_id]['currency']
            account['currency_symbol'] = getCurrencySymbol(account['currency'])
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
    
def getTransactions(connector, sort_by = 'time', reverse_order = False):
    '''
    Return transactions with ordering and sorting options
    '''
    transactions_ordered = []
    transactions = connector.listalltransactions()
    for provider_id in transactions.keys():
        for transaction in transactions[provider_id]:
            transaction['provider_id'] = provider_id
            transactions_ordered.append(transaction)
    
    transactions_ordered = sorted(transactions_ordered, key=lambda k: k.get(sort_by,0), reverse=reverse_order)
    return transactions_ordered

def getTransactionsByAccount(connector, account_name, provider_id, sort_by = 'time', reverse_order = False, count=10, start=0):
    '''
    Return transactions by account name and currency
    '''
    transactions = connector.listtransactionsbyaccount(account_name, provider_id, count, start)
    transactions_ordered = sorted(transactions, key=lambda k: k.get(sort_by,0), reverse=reverse_order)
    return transactions_ordered

def getSiteSections(active): 
    sections = config.MainConfig['site_sections']
    
    for section in sections:
        if section['name'] == active:
            section['active'] = True
        else:
            section['active'] = False
            
    return sections

def getCurrencySymbol(for_currency='*'):
    '''
    Return the currency symbol
    '''
    currencies = {}
    connection_config = connections.connector.config
    for provider_id in connection_config.keys():
        currencies[connections.connector.config[provider_id]['currency'].lower()] = connections.connector.config[provider_id]['symbol']
    
    if for_currency == '*':
        return currencies
    else:
        for_currency = for_currency.lower()
        return currencies[for_currency]

def buildBreadcrumbs(current_section='dashboard', currect_subsection='', current_activesection=''):
    # this is kind of stupid but it is 12 AM and I am sleepy
    breadcrumbs = []
    for section in config.MainConfig['site_sections']:
        if section['name'] == current_section:
            breadcrumbs.append({'name': section['title'], 'path': section['path']})
            for subsection in section.get('subsections', []):
                if subsection['name'] == currect_subsection:
                    breadcrumbs.append({'name': subsection['title'], 'path': subsection['path']})
                    
    if current_activesection:
        breadcrumbs.append({'name': current_activesection, 'path': "", 'active': True})
        
    return breadcrumbs
    
def prettyPrint(o):
    '''
    Print in a pretty way something
    '''
    try:
        import pprint 
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(o)
    except:
        print o
    
def isFloat(s):
    '''
    Check if s is float
    '''
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False
    
def humanBytes(num):
    '''
    Humanize bytes
    '''
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def getClientIp(request):
    '''
    Get client IP address
    '''
    
    x_forwarded_header = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_header:
        ip = x_forwarded_header.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def getInitialProviderId():
    '''
    Get the first provider id if it exists
    '''
    keys = connections.connector.config.keys()
    if keys:
        return keys[0]
    else:
        return 0
    
def b58encode(v):
    ''' 
    Encode v, which is a string of bytes, to base58.
    Source: https://github.com/bitcoin-abe/bitcoin-abe/blob/master/Abe/base58.py
    '''
    
    __b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    __b58base = len(__b58chars)
    
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += ord(c) << (8*i) # 2x speedup vs. exponentiation
    
    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result
    
    # Bitcoin does a little leading-zero-compression:
    # leading 0-bytes in the input become leading-1s
    nPad = 0
    for c in v:
        if c == '\0': nPad += 1
        else: break

    return (__b58chars[0]*nPad) + result