from jsonrpc import ServiceProxy
import datetime

class Connector(object):
    caching_time = 5
    config = {
        'ltc':  {
            'rpcusername': "testuser",
            'rpcpassword': "testnet",
            'rpchost': "sunflower",
            'rpcport': "7001",
            'currency_name': 'LiteCoin (LTC)',
        },
        'btc' :  {
            'rpcusername': "testuser",
            'rpcpassword': "testnet",
            'rpchost': "sunflower",
            'rpcport': "7000",
            'currency_name': 'BitCoin (BTC)',
        },
    }
    
    services = {}
    
    # caching data
    accounts = {'when': 0, 'data': None}
    transactions = {'when': 0, 'data': None}
    
    
    def __init__(self):
        for currency in self.config:
            self.services[currency] = ServiceProxy("http://%s:%s@%s:%s" % (self.config[currency]['rpcusername'], 
                                                                           self.config[currency]['rpcpassword'], 
                                                                           self.config[currency]['rpchost'], 
                                                                           self.config[currency]['rpcport'])
                                                  )

    def listaccounts(self):
        if self.accounts['data'] is not None and ((datetime.datetime.now() - self.accounts['when']).seconds < self.caching_time):
            return self.accounts['data']
        
        accounts = {}
        for currency in self.services.keys():
            accounts[currency] = self.services[currency].listaccounts()
        
        self.accounts['when'] = datetime.datetime.now()
        self.accounts['data'] = accounts
        return accounts
    
    def getaddressesbyaccount(self, name):
        addresses = []
        for currency in self.services.keys():
            addresses = addresses + self.services[currency].getaddressesbyaccount(name)
        return addresses
    
    def listtransactions(self, account=None):
        if self.transactions['data'] is not None and ((datetime.datetime.now() - self.transactions['when']).seconds < self.caching_time):
            return self.transactions['data']
        
        transactions = {}
        for currency in self.services.keys():
            if account is None or account is "":
                transactions[currency] = self.services[currency].listtransactions()
            else:
                transactions[currency] = self.services[currency].listtransactions(account)
                
        self.transactions['when'] = datetime.datetime.now()
        self.transactions['data'] = transactions
        return transactions
    
    def getnewaddress(self, currency, account_name):
        '''
        Create a new address
        '''
        new_address = self.services[currency].getnewaddress(account_name)
        return new_address
    
