class CoinAccount(object):
    '''
    Class for an account
    '''
    _account = {}
    _hidden = False
    
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
    
    def isDefault(self):
        if self._account['name'] == u"":
            self._hidden = True
            return True
        else:
            return False
    
    def isHidden(self):
        return self._hidden or self._account['hidden'] or self.isDefault()
    
    