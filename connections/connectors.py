from jsonrpc import ServiceProxy
import datetime
import generic
from accounts.models import accountFilter

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
        '''
        Constructor, load config 
        '''
        try:
            import config
            self.config = config.config
        except (AttributeError, ImportError) as e:
            self.errors.append({'message': 'Error occurred while compiling list of accounts (%s)' % (e)})
        
        for currency in self.config:
            self.services[currency] = ServiceProxy("http://%s:%s@%s:%s" % (self.config[currency]['rpcusername'], 
                                                                           self.config[currency]['rpcpassword'], 
                                                                           self.config[currency]['rpchost'], 
                                                                           self.config[currency]['rpcport'])
                                                  )

    def removeCurrencyService(self, currency):
        '''
        Remove the ServiceProxy objet from the list of service in case of a xxxcoind daemon not responding in time
        '''
        if self.services[currency]:
            del self.services[currency]

    def longNumber(self, x):
        '''
        Convert number coming from the JSON-RPC to a human readable format with 8 decimal
        '''
        return "{:.8f}".format(x)
    
    def listaccounts(self, gethidden=False, getarchived=False):
        '''
        Get a list of accounts. This method also add filtering, fetches address for each account etc.
        '''

        address_ignore_list = []
        if not getarchived:
            # get a list of archived address
            ignore_list = accountFilter.objects.filter(status=1)
            for ignored_account in ignore_list:
                address_ignore_list.append(ignored_account.address.encode('ascii'))
        
        address_hidden_list = []
        if not gethidden:
            # get a list of hidden accounts
            hidden_list = accountFilter.objects.filter(status=2)
            for hidden_account in hidden_list:
                address_hidden_list.append(hidden_account.address.encode('ascii'))
        
        # check for cached data, use that or get it again
        if self.accounts['data'] is not None and ((datetime.datetime.now() - self.accounts['when']).seconds < self.caching_time):
            cached_accounts = self.accounts['data']
        else:
            cached_accounts = {}
            for currency in self.services.keys():
                cached_accounts[currency] = self.services[currency].listaccounts()
            
            # caching result
            self.accounts['when'] = datetime.datetime.now()
            self.accounts['data'] = cached_accounts
        
        try:
            accounts = {}
            for currency in self.services.keys():
                accounts[currency] = []
                accounts_for_currency = self.accounts['data'][currency]
        
                for account_name, account_balance in accounts_for_currency.items():
                    account_addresses = self.getaddressesbyaccount(account_name, currency)
                    
                    # check all addresses if they are in the archive list
                    for ignored_address in address_ignore_list:
                        if ignored_address in account_addresses:
                            del account_addresses[account_addresses.index(ignored_address)]
                    
                    # check all addresses if they are in the hidden list
                    hidden_flag = False
                    for hidden_address in address_hidden_list:
                        if hidden_address in account_addresses:
                            hidden_flag = True
                    
                    # catch default address without name
                    if account_name == "":
                        alternative_name = '(no name)'
                    else:
                        alternative_name = account_name
                    
                    # if there any address left then add it to the list
                    if account_addresses:
                        accounts[currency].append({
                                                   'name': account_name, 
                                                   'balance': self.longNumber(account_balance), 
                                                   'addresses': account_addresses, 
                                                   'hidden': hidden_flag,
                                                   'alternative_name': alternative_name,
                                                   'currency': currency.upper(),
                                                   })
                    
        except Exception as e:
            self.errors.append({'message': 'Error occurred while compiling list of accounts (currency: %s, error:%s)' % (currency, e)})
            self.removeCurrencyService(currency)
            return self.accounts['data']
        
        return accounts
    
    def getaddressesbyaccount(self, name, currency):
        '''
        Get the address of an account name
        '''
        if self.services[currency]:
            addresses = self.services[currency].getaddressesbyaccount(name)
            address_str = []
            for address in addresses:
                address_str.append(address.encode('ascii','ignore'))
        else:
            address_str = []
        return address_str
    
    def listtransactionsbyaccount(self, account_name, currency):    
        '''
        Get a list of transactions by account and currency
        '''  
        transactions = []
        try:
            transactions = self.services[currency].listtransactions(account_name, 1000000, 0)
            for transaction in transactions:
                transaction['timereceived_pretty'] = generic.twitterizeDate(transaction.get('timereceived', 'never'))
                transaction['time_pretty'] = generic.twitterizeDate(transaction.get('time', 'never'))
                transaction['timereceived_human'] = datetime.datetime.fromtimestamp(transaction.get('timereceived', 0))
                transaction['time_human'] = datetime.datetime.fromtimestamp(transaction.get('time', 0))
                transaction['currency'] = currency
        except Exception as e:
            self.errors.append({'message': 'Error occurred while compiling list of transactions (%s)' % (e)})
            self.removeCurrencyService(currency)
            
        return transactions
    
    def listtransactions(self):
        ''' 
        Get a list of transactions
        '''
        
        if self.transactions['data'] is not None and ((datetime.datetime.now() - self.transactions['when']).seconds < self.caching_time):
            return self.transactions['data']
        
        accounts = self.listaccounts(gethidden=True, getarchived=True)
        
        try:
            transactions = {}
            for currency in accounts.keys():
                transactions[currency] = []
                for account in accounts[currency]:
                    # append list
                    transactions[currency] = transactions[currency] + self.listtransactionsbyaccount(account['name'], currency)
        except Exception as e:
            self.errors.append({'message': 'Error occurred while compiling list of transactions (%s)' % (e)})
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
        '''
        Get balance for each currency
        '''
        
        if self.balances['data'] is not None and ((datetime.datetime.now() - self.balances['when']).seconds < self.caching_time):
            return self.balances['data']
        
        try:
            balances = {}
            for currency in self.services.keys():
                balances[currency] = generic.longNumber(self.services[currency].getbalance())
        except Exception as e:
            self.errors.append({'message': 'Error occurred while getting balances (currency: %s, error: %s)' % (currency, e)})
            self.removeCurrencyService(currency)
            return self.transactions['data']
        
        self.balances['when'] = datetime.datetime.now()
        self.balances['data'] = balances
        return balances
    
    
    def getaccountdetailsbyaddress(self, address):
        '''
        Return account details 
        '''
        
        accounts = self.listaccounts(gethidden=True, getarchived=True)
        
        target_account = None
        for currency in accounts.keys():
            for account in accounts[currency]:
                if address in account['addresses']:
                    target_account = account
                    target_account['currency'] = currency
                    break
        return target_account
            
        
        
