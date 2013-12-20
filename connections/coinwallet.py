import connections

class CoinWallet(object):
    '''
    Class for a wallet
    '''
    _config = {}

    def __init__(self, wallet_config):
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
    
    def balance(self):
        '''
        Get wallet balance
        '''
        balance = connections.connector.getbalance(self.provider_id)
        return balance[self.provider_id]
    
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
    
    def getTransactions(self, limit=10, start=0):
        '''
        Return a list of transactions wallet-wide
        '''
        transactions = connections.connector.listtransactionsbyaccount("*", self.provider_id, limit, start)
        return transactions
    