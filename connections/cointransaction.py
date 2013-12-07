import sys
connections = sys.modules['connections']

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
        '''
        # catch default accounts
        if key in [u'otheraccount', u'account']:
            if transaction[key] is u"":
                default_account = connections.connector.getdefaultaccount(transaction['provider_id'])
                if key == u'account':
                    transaction['account'] = '(default account)'
                    transaction['destination_addresses'] = default_account['addresses']
                elif key == u'otheraccount':
                    transaction['otheraccount'] = '(default account)'
                    transaction['source_addresses'] = default_account['addresses']
        '''       
        
        return transaction[key]
     
    def __setitem__(self, key, value):
        transaction = getattr(self, '_transaction')
        transaction[key] = value
        return setattr(self, '_transaction', transaction)
    
    def get(self, key, default=False):
        if self._transaction.get(key, False):
            return self._transaction.get(key, False)
        else:
            return default
        