from django import template

from mybitbank.libs.entities.coinaccount import CoinAccount
from mybitbank.libs.entities.coinaddress import CoinAddress


def keyvalue(value, arg):
    '''
    Template tag to fetch value from key
    '''
    try:
        return value[arg]
    except:
        return False

def getalerticon(arg):
    '''
    Template tag to use proper icon for alert messages
    '''
    types = {
             'info': 'info-sign',
             'alert': 'remove',
             'warning': 'exclamation-sign',
             'success': 'ok'
             }
    return types[arg]

def getaccountname(account):
    '''
    Template tag to catch account aliases and default "noname" accounts
    '''
    if isinstance(account, CoinAccount):
        if account.haskey('alias'):
            return account.get('alias')
        elif account.haskey('name'):
            if account.isDefault():
                return "main account"
            else:
                return account.get('name')
        else:
            return "no account name"
    else:
        return "not CoinAccount"
    
def getaddressbookname(address):
    '''
    Template tag to return the address book entry name
    '''
    
    if isinstance(address, CoinAddress):
        address_book_name = address.getAddressBookName()
        if address_book_name:
            return address_book_name
        else:
            return None

def getnumberofalert(system_alerts):
    '''
    Measure the number of system alerts
    '''
    num = 0
    for system_alert_type, system_alert_per_type in system_alerts.items():
        for system_alert in system_alert_per_type:
            num += 1
    return num
    

register = template.Library()
register.filter('keyvalue', keyvalue)
register.filter('getalerticon', getalerticon)
register.filter('getaccountname', getaccountname)
register.filter('getaddressbookname', getaddressbookname)
register.filter('getnumberofalert', getnumberofalert)
