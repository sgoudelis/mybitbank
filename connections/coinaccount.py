import connections
import generic
import hashlib

class CoinAccount(object):
    '''
    Class for an account
    '''
    _account = {}
    _hidden = False
    
    def __init__(self, accountDetails):
        if type(accountDetails) is dict:
            self._account = accountDetails
            self._provider_id = accountDetails['provider_id']
            
    @property
    def provider_id(self):
        '''
        Property for the provider id
        '''
        return self.get('id', None)
           
    def __getitem__(self, key):
        '''
        Getter for dictionary-line behavior
        '''

        if key == "addresses":
            return self.getAddresses()
        elif key == "last_activity":
            return self.getLastActivity()
        elif key == "currency_symbol":
            return self.getCurrencySymbol()
        elif key == "currency_code":
            return self.getCurrencyCode()
        elif key == 'identifier':
            return self.getIdentifier()

        account = getattr(self, '_account')
        return account.get(key, None)
     
    def __setitem__(self, key, value):
        '''
        Setter for dictionary-line behavior
        '''
        account = getattr(self, '_account')
        account[key] = value
        return setattr(self, '_account', account)
    
    def get(self, key, default=False):
        '''
        Getter for dictionary-line behavior
        '''
        if self._account.get(key, False):
            return self._account.get(key, False)
        else:
            return default
        
    def haskey(self, key):
        '''
        Check the existence of key
        '''
        if key in self._account.keys():
            return True
        else:
            return False
    
    def getIdentifier(self):
        '''
        There is no unique identifier for an account in a xxxcoind daemon
        so lets make one. Hopefully the below hashing method will uniquely 
        identify an account for us
        '''
        unique_string = "provider_id=%s&name=%s&currency=%s" % (self['provider_id'], self['name'], self['currency'])
        identifier = hashlib.sha1(unique_string).hexdigest()
        return identifier
        
    def isDefault(self):
        '''
        Return bool whether this is a default account or not
        '''
        if self._account['name'] == u"":
            self._hidden = True
            return True
        else:
            return False
    
    def getBalance(self):
        '''
        Return the account balance
        '''
        balance = connections.connector.getbalance(self.provider_id, self['name'])
        return generic.longNumber(balance)
    
    def isHidden(self):
        '''
        Return bool if this account is hidden
        '''
        return self._hidden or self._account['hidden'] or self.isDefault()
    
    def getAddresses(self):
        '''
        Return a list of addresses for this account
        '''
        addressess = connections.connector.getaddressesbyaccount(self['name'], self['provider_id'])
        return addressess
    
    def getAddressesCount(self):
        '''
        Return the number of address under this account
        '''
        addresses = self.getAddresses()
        return len(addresses)
    
    def getLastActivity(self):
        '''
        Return the date of the last activity
        '''
        transactions = connections.connector.listtransactionsbyaccount(self['name'], self['provider_id'], 1, 0)
        if transactions:
            last_activity = generic.twitterizeDate(transactions[0]['time'])
        else:
            last_activity = "never"
            
        self['last_activity'] = last_activity
        return last_activity
    
    def getCurrencySymbol(self):
        '''
        Return the Unicode currency symbol
        '''
        return generic.getCurrencySymbol(self.getCurrencyCode())
    
    def getCurrencyCode(self):
        '''
        Return the currency code
        '''
        return self.get('currency', "").lower()
    
    def getTransactions(self, sort_by='time', reverse_order=False, count=10, start=0):
        '''
        Return transactions list for account
        '''
        transactions = connections.connector.listtransactionsbyaccount(self['name'], self['provider_id'], count, start)
        transactions_ordered = sorted(transactions, key=lambda k: k.get(sort_by,0), reverse=reverse_order)
        return transactions_ordered
    