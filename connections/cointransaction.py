class CoinTransaction(object):
    '''
    Class for a transaction
    '''
    _transaction = {}
    
    def __init__(self, transactionDetails):
        if type(transactionDetails) is dict:
            self._transaction = transactionDetails
            
    def __getitem__(self, key):
        transaction = getattr(self, '_transaction')
        return transaction[key]
     
    def __setitem__(self, key, value):
        transaction = getattr(self, '_transaction')
        transaction[key] = value
        return setattr(self, '_transaction', transaction)
    
    def get(self, key, default):
        if self._transaction.get(key, False):
            return self._transaction.get(key, False)
        else:
            return default
        