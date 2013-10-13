from jsonrpc import ServiceProxy
import datetime
from lib import longNumber

class Connector(object):
    caching_time = 5
    config = []
    
    '''
        config = {
        'btc' :  {
            'rpcusername': "testuser",
            'rpcpassword': "testnet",
            'rpchost': "sunflower",
            'rpcport': "7000",
            'currency_name': 'BitCoin (BTC)',
        },
        'ltc':  {
            'rpcusername': "testuser",
            'rpcpassword': "testnet",
            'rpchost': "sunflower",
            'rpcport': "7001",
            'currency_name': 'LiteCoin (LTC)',
        },
    }
    '''
    services = {}
    errors = []
    
    # caching data
    accounts = {'when': datetime.datetime.fromtimestamp(0), 'data': {}}
    transactions = {'when': datetime.datetime.fromtimestamp(0), 'data': {}}
    balances = {'when': datetime.datetime.fromtimestamp(0), 'data': {}}
    
    def __init__(self):
        # load config
        try:
            import config
            self.config = config.config
        except (AttributeError, ImportError) as e:
            self.errors.append({'message': 'Error occured while compiling list of accounts (%s)' % (e)})
        
        for currency in self.config:
            self.services[currency] = ServiceProxy("http://%s:%s@%s:%s" % (self.config[currency]['rpcusername'], 
                                                                           self.config[currency]['rpcpassword'], 
                                                                           self.config[currency]['rpchost'], 
                                                                           self.config[currency]['rpcport'])
                                                  )

    def removeCurrencyService(self, currency):
        del self.services[currency]

    def longNumber(self, x):
        '''
        Convert number coming from the JSON-RPC to a human readable format with 8 decimal
        '''
        return "{:.8f}".format(x)
    
    def listaccounts(self):
        if self.accounts['data'] is not None and ((datetime.datetime.now() - self.accounts['when']).seconds < self.caching_time):
            return self.accounts['data']
        
        try:
            accounts = {}
            for currency in self.services.keys():
                accounts[currency] = []
                accounts_for_currency = self.services[currency].listaccounts()
                for account_name, account_balance in accounts_for_currency.items():
                    account_addresses = self.getaddressesbyaccount(account_name, currency)
                    if account_addresses:
                        account_address = account_addresses[0]
                    else:
                        account_address = ""
                    accounts[currency].append({'name': account_name, 'balance': self.longNumber(account_balance), 'address': account_address})
                    
        except Exception as e:
            self.errors.append({'message': 'Error occured while compiling list of accounts (currency: %s, error:%s)' % (currency, e)})
            self.removeCurrencyService(currency)
            return self.accounts['data']
        
        self.accounts['when'] = datetime.datetime.now()
        self.accounts['data'] = accounts
        return accounts
    
    def getaddressesbyaccount(self, name, currency):
        if self.services[currency]:
            addresses = self.services[currency].getaddressesbyaccount(name)
        else:
            addresses = []
        return addresses
    
    def listtransactions(self, account=None):
        if self.transactions['data'] is not None and ((datetime.datetime.now() - self.transactions['when']).seconds < self.caching_time):
            return self.transactions['data']
        
        try:
            transactions = {}
            for currency in self.services.keys():
                if account is None or account is "":
                    transactions[currency] = self.services[currency].listtransactions()
                else:
                    transactions[currency] = self.services[currency].listtransactions(account)
        except Exception as e:
            self.errors.append({'message': 'Error occured while compiling list of accounts (%s)' % (e)})
            self.removeCurrencyService(currency)
            return self.transactions['data']
        
        self.transactions['when'] = datetime.datetime.now()
        self.transactions['data'] = transactions
        return transactions
    
    def getnewaddress(self, currency, account_name):
        '''
        Create a new address
        '''
        if self.services[currency]:
            new_address = self.services[currency].getnewaddress(account_name)
        else:
            new_address = None
        return new_address
    
    def getbalance(self):
        if self.balances['data'] is not None and ((datetime.datetime.now() - self.balances['when']).seconds < self.caching_time):
            return self.balances['data']
        
        try:
        
            balances = {}
            for currency in self.services.keys():
                balances[currency] = longNumber(self.services[currency].getbalance())
        except Exception as e:
            self.errors.append({'message': 'Error occured while getting balances (currency: %s, error: %s)' % (currency, e)})
            self.removeCurrencyService(currency)
            return self.transactions['data']
        
        self.balances['when'] = datetime.datetime.now()
        self.balances['data'] = balances
        return balances
        
        
    
