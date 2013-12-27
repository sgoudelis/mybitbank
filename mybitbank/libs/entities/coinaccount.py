import hashlib

from cacher import Cacher
from coinaddress import CoinAddress
from cointransaction import CoinTransaction
from mybitbank.libs import misc
from mybitbank.libs.connections import connector


class CoinAccount(object):
    '''
    Class for an account
    '''
    
    def __init__(self, accountDetails):
        self._errors = []
        self._account = {}
        self._hidden = False
        self._cache = Cacher({
         'transactions': {},
         'balances': {},
         'addressesbyaccount': {},
         })
        
        if type(accountDetails) is dict:
            self._account = accountDetails
            self._provider_id = accountDetails['provider_id']
            
    @property
    def provider_id(self):
        '''
        Property for the provider id
        '''
        return self.get('provider_id', None)
           
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
    
    def getParamHash(self, param=""):
        '''
        This function takes a string and calculates a sha224 hash out of it. 
        It is used to hash the input parameters of functions/method in order to 
        uniquely identify a cached result based  only on the input parameters of 
        the function/method call.
        '''
        cache_hash = hashlib.sha224(param).hexdigest()
        return cache_hash
    
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
        balance = connector.getBalance(self.provider_id, self['name'])
        return misc.longNumber(balance)
    
    def isHidden(self):
        '''
        Return bool if this account is hidden
        '''
        return self._hidden or self._account['hidden'] or self.isDefault()
    
    def getAddresses(self):
        '''
        Get the address for an account name
        '''
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("name=%s" % (self['name']))
        cached_object = self._cache.fetch('addressesbyaccount', cache_hash)
        if cached_object:
            return cached_object
        
        addresses = connector.getAddressesByAccount(self['name'], self.provider_id)
        addresses_list = []
        for address in addresses:
            coinaddr = CoinAddress(address, self)
            addresses_list.append(coinaddr)
            
        # cache the result
        self._cache.store('addressesbyaccount', cache_hash, addresses_list)
        return addresses_list
    
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
        last_transaction = self.listTransactions(1, 0)
        if last_transaction:
            last_activity = misc.twitterizeDate(last_transaction[0]['time'])
        else:
            last_activity = "never"
            
        self['last_activity'] = last_activity
        return last_activity
    
    def getCurrencySymbol(self):
        '''
        Return the Unicode currency symbol
        '''
        return misc.getCurrencySymbol(connector, self.getCurrencyCode())
    
    def getCurrencyCode(self):
        '''
        Return the currency code
        '''
        return self.get('currency', "").lower()
    
    def listTransactions(self, limit=100000, start=0, orderby='time', reverse=True):    
        '''
        Get a list of transactions by account name and provider_id
        '''

        cache_hash = self.getParamHash("limit=%s&start=%sorderby=%s&reverse=%s" % (limit, start, orderby, reverse))
        cached_object = self._cache.fetch('transactions', cache_hash)
        if cached_object:
            return cached_object
        
        transactions = []
        transaction_list = connector.listTransactionsByAccount(self['name'], self['provider_id'], limit, start)
        
        for entry in transaction_list:
            if entry.get('address', False):
                entry['address'] = CoinAddress(entry['address'], self)
            
            # give out a provider id and a currency code to the transaction dict
            entry['provider_id'] = self.provider_id
            entry['currency'] = self['currency']
            
            if entry['category'] == 'receive':
                entry['source_address'] = CoinAddress(entry.get('details', {}).get('sender_address', False), "This is a sender address!")
            elif entry['category'] == 'send':
                entry['source_addresses'] = self['wallet'].getAddressesByAccount(entry['account'])
            
            entry['wallet'] = self['wallet']
            
            coin_transaction = CoinTransaction(entry)
            transactions.append(coin_transaction)
            
        # sort result
        transactions = sorted(transactions, key=lambda transaction: transaction[orderby], reverse=reverse) 
            
        # cache the result
        self._cache.store('transactions', cache_hash, transactions)
        return transactions
    
    