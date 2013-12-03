class CoinAccount(object):
    '''
    Class for an account
    '''
    _account = {}
    
    def __init__(self, accountDetails):
        if type(accountDetails) is dict:
            self._account = accountDetails
            
    def __getitem__(self, key):
        account = getattr(self, '_account')
        return account[key]
     
    def __setitem__(self, key, value):
        account = getattr(self, '_account')
        account[key] = value
        return setattr(self, '_account', account)
    
    def get(self, key, default=False):
        if self._account.get(key, False):
            return self._account.get(key, False)
        else:
            return default
