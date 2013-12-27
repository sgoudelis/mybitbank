import hashlib

from mybitbank.apps.accounts.models import accountFilter
from mybitbank.libs.connections import connector
from cacher import Cacher
from coinaddress import CoinAddress
from cointransaction import CoinTransaction
from coinaccount import CoinAccount

class CoinWallet(object):
    '''
    Class for a wallet
    '''
    def __init__(self, wallet_config):
        self._errors = []
        self._config = {}
        self._cache = Cacher({
             'accounts': {},
             'transactions': {},
             'transactiondetails': {},
             'balances': {},
             'info': {},
             })
        
        if type(wallet_config) is dict:
            self._config = wallet_config
        
    @property
    def provider_id(self):
        '''
        Property for the provider id
        '''
        return self.get('id', None)
    
    @property
    def enabled(self):
        '''
        Return the status (enabled/disabled)
        '''
        return self.get('enabled', False)
    
    def __getitem__(self, key):
        '''
        Getter for dictionary-line behavior
        '''
        if key == "currency_symbol":
            return self.getCurrencySymbol()
        elif key == "currency_code":
            return self.getCurrencyCode()
        
        config = getattr(self, '_config')
        return config[key]
     
    def __setitem__(self, key, value):
        '''
        Setter for dictionary-line behavior
        '''
        config = getattr(self, '_config')
        config[key] = value
        return setattr(self, '_config', config)
    
    def get(self, key, default=False):
        '''
        Implementing .get() method for dictionary-line behavior
        '''
        if self._config.get(key, False):
            return self._config.get(key, False)
        else:
            return default
    
    def haskey(self, key):
        '''
        Check the existence of key
        '''
        if key in self._config.keys():
            return True
        else:
            return False
    
    def getNet(self):
        '''
        Return network value, mainnet or testnet
        '''
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("provider_id=%s" % self.provider_id)
        cached_peerinfo = self._cache.fetch('info', cache_hash)
        if cached_peerinfo:
            info = cached_peerinfo
        else:
            info = connector.getinfo(self.provider_id)
            self._cache.store('info', cache_hash, info)
        
        is_testnet = False
        if info.has_key('testnet'):
            is_testnet = info.get('testnet')
            if is_testnet is False:
                return "mainnet"
            elif is_testnet is True:
                return "testnet"
        else:
            # default to mainnet
            return "mainnet"
    
    def balance(self):
        '''
        Get wallet balance
        '''
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("balance")
        cached_object = self._cache.fetch('balance', cache_hash)
        if cached_object:
            return cached_object.get(self.provider_id, "-")
        
        balance = connector.getBalance(self.provider_id)

        # store result in cache
        self._cache.store('balance', cache_hash, balance)
        
        return balance.get(self.provider_id, "-")
    
    def getParamHash(self, param=""):
        '''
        This function takes a string and calculates a sha224 hash out of it. 
        It is used to hash the input parameters of functions/method in order to 
        uniquely identify a cached result based  only on the input parameters of 
        the function/method call.
        '''
        cache_hash = hashlib.sha224(param).hexdigest()
        return cache_hash
    
    def listAccounts(self, gethidden=False, getarchived=False):
        '''
        Get a list of accounts. This method also supports filtering, fetches address for each account etc.
        '''
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("gethidden=%s&getarchived=%s" % (gethidden, getarchived))
        cached_object = self._cache.fetch('accounts', cache_hash)
        if cached_object:
            return cached_object
        
        # get data from the connector (xxxcoind)
        fresh_accounts = connector.listAccounts(gethidden=False, getarchived=False, selected_provider_id=self.provider_id)

        # get a list of archived address
        address_ignore_list = []
        if not getarchived:
            ignore_list = accountFilter.objects.filter(status=1)
            for ignored_account in ignore_list:
                address_ignore_list.append(ignored_account.address.encode('ascii'))
        
        # get a list of hidden accounts
        address_hidden_list = []
        if not gethidden:
            hidden_list = accountFilter.objects.filter(status=2)
            for hidden_account in hidden_list:
                address_hidden_list.append(hidden_account.address.encode('ascii'))
        
        accountObjects = []
        for account_name, account_balance in fresh_accounts.get(self.provider_id, {}).items():

            '''
            # check all addresses if they are in the archive list
            for ignored_address in address_ignore_list:
                if ignored_address in account_addresses:
                    del account_addresses[account_addresses.index(ignored_address)]
            
            # check all addresses if they are in the hidden list
            hidden_flag = False
            for hidden_address in address_hidden_list:
                if hidden_address in account_addresses:
                    hidden_flag = True
            '''
            
            accountObjects.append(CoinAccount({
                                       'name': account_name, 
                                       'balance': account_balance, 
                                       'currency': self['currency'],
                                       'provider_id': self.provider_id,
                                       'wallet': self,
                                       }))
        
        # cache the result
        self._cache.store('accounts', cache_hash, accountObjects)
        return accountObjects
    
    def getCurrencySymbol(self):
        '''
        Return the Unicode currency symbol
        '''
        return self.get('symbol', None)
    
    def getCurrencyCode(self):
        '''
        Return the currency code
        '''
        return self.get('currency', "").lower()
    
    def listTransactions(self, limit=10, start=0):
        '''
        Return a list of transactions wallet-wide
        '''
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("limit=%s&start=%s" % (limit, start))
        cached_object = self._cache.fetch('transactions', cache_hash)
        if cached_object:
            return cached_object
        
        transactions = []
        transactions_dicts = connector.listTransactionsByAccount("*", self.provider_id, limit, start)
        for transaction in transactions_dicts:
            transaction['wallet'] = self
            transaction['currency'] = self.getCurrencyCode()
            transaction['currency_symbol'] = self.getCurrencySymbol()
            transaction['provider_id'] = self.provider_id
            transactions.append(CoinTransaction(transaction))
        
        self._cache.store('transactions', cache_hash, transactions)
        return transactions
    
    def getAccountByName(self, name):
        '''
        Return CoinAccount() for name
        '''
        accounts = self.listAccounts(gethidden=True, getarchived=True)
        for account in accounts:
            if account['name'] == name:
                return account
        
        return None
    
    def getTransactionById(self, txid):
        '''
        Return a transaction by txid
        '''
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("txid=%s" % (txid))
        cached_object = self._cache.fetch('transactiondetails', cache_hash)
        if cached_object:
            return cached_object
        
        transaction_details = connector.getTransaction(txid, self.provider_id)
        transaction_details['currency'] = self.getCurrencyCode()
        transaction_details['wallet'] = self
        
        self._cache.store('transactiondetails', cache_hash, transaction_details)
        return CoinTransaction(transaction_details)
    
    def getAddressesByAccount(self, account):
        '''
        Get a list of address for account
        '''
        addresses_list = connector.getAddressesByAccount(account, self.provider_id)
        coinaddresses = []
        for address in addresses_list:
            coinaddresses.append(CoinAddress(address, account))
            
        return coinaddresses
    
    def getDefaultAccount(self):
        '''
        Return the CoinAccount object for the default wallet account
        '''
        accounts = self.listAccounts(gethidden=True, getarchived=True)
        for account in accounts:
            if len(account['name']) == 0:
                return account
        else:
            return None
        
    def getAccountByAddress(self, address):
        '''
        Return account by address
        '''
        accounts = self.listAccounts(gethidden=True, getarchived=True)
        
        target_account = None
        for account in accounts:
            for account_address in account['addresses']:
                if str(address) == str(account_address):
                    target_account = account
                    target_account['currency'] = self.getCurrencyCode()
                    target_account['provider_id'] = self.provider_id
                    return target_account
        else:
            return None
        
    def getAccountByIdentifier(self, identifier):
        '''
        Get account by identifier
        '''
        list_of_accounts = self.listAccounts(gethidden=True, getarchived=True)
        for account in list_of_accounts:
            if account.getIdentifier() == identifier:
                return account
        else:
            return None
        
    