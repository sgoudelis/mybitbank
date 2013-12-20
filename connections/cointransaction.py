import connections
import generic
import config

class CoinTransaction(object):
    '''
    Class for a transaction
    '''
    
    _transaction = {}
    
    def __init__(self, transactionDetails):
        if type(transactionDetails) is dict:
            self._transaction = transactionDetails
            
            if self.get('category', False) in ['receive','send']:
                if self['confirmations'] <= config.MainConfig['globals']['confirmation_limit']:
                    self['status_icon'] = 'glyphicon-time'
                    self['status_color'] = '#AAA';
                    self['tooltip'] = self['confirmations']
                else:
                    self['status_icon'] = 'glyphicon-ok-circle'
                    self['status_color'] = '#1C9E3F';
                    self['tooltip'] = self['confirmations']
            
            if self['category'] == 'receive':
                self['icon'] = 'glyphicon-circle-arrow-down'
                self['account'] = generic.getAccountByName(connections.connector, self['provider_id'], self['account'])
            elif self['category'] == 'send':
                self['icon'] = 'glyphicon-circle-arrow-up'
                self['account'] = generic.getAccountByName(connections.connector, self['provider_id'], self['account'])
            elif self['category'] == 'move':
                
                self['icon'] = 'glyphicon-circle-arrow-right'  
                self['account'] = generic.getAccountByName(connections.connector, self['provider_id'], self['account'])
                self['otheraccount'] = generic.getAccountByName(connections.connector, self['provider_id'], self['otheraccount'])
            
    def __getitem__(self, key):
        transaction = getattr(self, '_transaction')
        
        if key == 'category':
            try:
                return self._transaction['details'][0]['category']
            except:
                return self._transaction['category']
        if key == "currency_symbol":
            return self.getCurrencySymbol()
        elif key == "currency_code":
            return self.getCurrencyCode()
        
        return transaction.get(key, None)
     
    def __setitem__(self, key, value):
        transaction = getattr(self, '_transaction')
        transaction[key] = value
        return setattr(self, '_transaction', transaction)
    
    def get(self, key, default=False):
        if self._transaction.get(key, False):
            return self._transaction.get(key, False)
        else:
            return default
        
    def haskey(self, key):
        '''
        Check the existence of key
        '''
        if key in self._transaction.keys():
            return True
        else:
            return False

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
    