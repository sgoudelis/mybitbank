from jsonrpc import ServiceProxy
import datetime
import generic
from accounts.models import accountFilter
from bitcoinrpc.authproxy import JSONRPCException
from django.template.defaultfilters import time

class Connector(object):
    # how long to cache responses
    caching_time = 3 
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
    
    # source: https://github.com/zamgo/PHPCoinAddress/blob/master/README.md
    prefixes = {
                'btc': {'mainnet': '\x00', 'testnet': '\x6f'},
                'ltc': {'mainnet': '\x30', 'testnet': '\x6f'},
                'ftc': {'mainnet': '\x0E', 'testnet': '\x6f'},
                'ppc': {'mainnet': '\x37', 'testnet': '\x6f'},
                'nmc': {'mainnet': '\x34', 'testnet': '\x6f'},
                'nvc': {'mainnet': '\x08', 'testnet': '\x6f'},
               }
    
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

    def getNet(self, currency):
        return self.config[currency].get('network', 'testnet')

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
            #raise
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
        except Exception as e:
            #raise
            self.errors.append({'message': 'Error occurred while compiling list of transactions (%s) while doing listtransactions()' % (e.error)})
            self.removeCurrencyService(currency)
            
        for transaction in transactions:
            transaction['timereceived_pretty'] = generic.twitterizeDate(transaction.get('timereceived', 'never'))
            transaction['time_pretty'] = generic.twitterizeDate(transaction.get('time', 'never'))
            transaction['timereceived_human'] = datetime.datetime.fromtimestamp(transaction.get('timereceived', 0))
            transaction['time_human'] = datetime.datetime.fromtimestamp(transaction.get('time', 0))
            transaction['currency'] = currency
            if transaction.get('txid', False):
                transaction_details = self.gettransactiondetails(transaction['txid'], currency)
                if not transaction_details.get('code', False):
                    transaction['details'] = transaction_details
                else:
                    self.errors.append({'message': transaction_details})
            
        return transactions
    
    def listtransactions(self):
        ''' 
        Get a list of transactions
        '''
        
        if self.transactions['data'] is not None and ((datetime.datetime.now() - self.transactions['when']).seconds < self.caching_time):
            return self.transactions['data']
        
        accounts = self.listaccounts(gethidden=True, getarchived=True)

        transactions = {}
        for currency in accounts.keys():
            transactions[currency] = []
            for account in accounts[currency]:
                # append list
                transactions[currency] = transactions[currency] + self.listtransactionsbyaccount(account['name'], currency)

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
            #raise
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

    def moveamount(self, from_account, to_account, currency, amount, minconf=1, comment=""):
        if not from_account or not to_account or not currency:
            return {'message': 'invalid input data'}
        
        account_list = self.listaccounts(True, True)
        
        account_names = []
        for account in account_list[currency]:
            account_names.append(account['name'])
        
        if from_account in account_names and to_account in account_names:
            # both accounts have being found, perform the move
            try:
                reply = self.services[currency].move(from_account, to_account, amount, minconf, comment)
            except JSONRPCException, e: 
                return e.error
            except ValueError, e:
                return {'message': e, 'code':-1}
            
            return reply
        else:
            # account not found
            return {'message': 'source account not found'}
              
    def sendfrom(self, from_account, to_address, amount, currency, minconf=1, comment="", comment_to=""):
        if not from_account or not to_address or not currency:
            return {'message': 'invalid input data'}
        
        account_list = self.listaccounts(True, True)
        
        account_names = []
        for account in account_list[currency]:
            account_names.append(account['name'])
            
        if from_account in account_names:
            # account given exists, continue
            try:
                reply = self.services[currency].sendfrom(from_account, to_address, amount, minconf, comment, comment_to)
            except JSONRPCException, e: 
                return e.error
            except ValueError, e:
                return {'message': e, 'code': -1}
            return reply
        else:
            # account not found
            return {'message': 'source account not found'}


    def gettransactiondetails(self, txid, currency):
        if not txid or not currency:
            return {}
        
        transaction_details = None
        try:
            transaction_details = self.services[currency].getrawtransaction(txid, 1)
        except JSONRPCException:
            return {}
        
        return {'sender_address': self.decodeScriptSig(transaction_details, currency, self.getNet(currency))}
        
    def decodeScriptSig(self, rawtransaction, currency, net='testnet'):
        '''
        Decode input script signature, courtesy of:
        http://bitcoin.stackexchange.com/questions/7838/why-does-gettransaction-report-me-only-the-receiving-address/8864#8864
        '''
        try:
            import hashlib
            import base58
        except:
            return None
        
        try:
            script_sig = rawtransaction['vin'][0]['scriptSig']['asm']
        except:
            return None
        
        script = script_sig.split()
        
        h = hashlib.sha256(script[1].decode("hex")).digest()
        ripe160 =  hashlib.new('ripemd160')
        ripe160.update(h)
        d = ripe160.digest()
        
        prefix = self.prefixes[currency][net]
        address = (prefix + d)
        
        # calculate checksum
        checksum = hashlib.sha256(hashlib.sha256(address).digest()).digest()[:4]
        
        # build the raw address
        address += checksum
        
        # encode the address in base58
        encoded_address = base58.b58encode(address)
        #print "resolved address: %s" % encoded_address
        
        return encoded_address
        
