import datetime
import generic
import hashlib
from jsonrpc import ServiceProxy
from connections.cacher import Cacher 
from accounts.models import accountFilter
from bitcoinrpc.authproxy import JSONRPCException


class Connector(object):
    # how long to cache responses
    caching_time = 10
    disable_time = 10
    config = {}
    services = {}
    errors = []
    alerts = []
    
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
    cache = None
    
    def __init__(self):
        '''
        Constructor, load config 
        '''
        print "Connector class initializing..."
        self.cache = Cacher({
             'accounts': {},
             'transactions': {},
             'balances': {},
             'addressesbyaccount': {},
             })
        try:
            import config
            self.config = config.config
        except (AttributeError, ImportError) as e:
            self.errors.append({'message': 'Error occurred while compiling list of accounts (%s)' % (e), 'when': datetime.datetime.utcnow()})
        
        for currency in self.config:
            self.services[currency] = ServiceProxy("http://%s:%s@%s:%s" % (self.config[currency]['rpcusername'], 
                                                                           self.config[currency]['rpcpassword'], 
                                                                           self.config[currency]['rpchost'], 
                                                                           self.config[currency]['rpcport'])
                                                  )
            # true is enabled, anything but bool is disabled up to the value as a timestamp
            # this will caught by the Middleware
            self.config[currency]['enabled'] = True
            
    def getNet(self, currency):
        return self.config[currency].get('network', 'testnet')

    def removeCurrencyService(self, currency):
        '''
        Remove the ServiceProxy object from the list of service in case of a xxxcoind daemon not responding in time
        '''
        if self.services.get(currency, False):
            self.alerts.append({'type': 'currencybackend', 'currency': currency, 'message': 'Currency service for %s is disabled for %s secs due an error communicating.' % (currency.upper(), self.disable_time), 'when': datetime.datetime.utcnow()})
            self.config[currency]['enabled'] = datetime.datetime.utcnow() + datetime.timedelta(0,self.disable_time)
            del self.services[currency]

    def longNumber(self, x):
        '''
        Convert number coming from the JSON-RPC to a human readable format with 8 decimal
        '''
        return "{:.8f}".format(x)
    
    def getpeerinfo(self, currency):
        # get data from the connector (coind)
        peers = []
        try:
            if self.config[currency]['enabled'] is True:
                peers = self.services[currency].getpeerinfo()
        except JSONRPCException:
            # in case coind not support getpeerinfo command
            return {'error'} 
        except Exception, e:
            # in case of an error, store the error, disabled the service and move on
            self.errors.append({'message': 'Error occurred while getting peers info of accounts (currency: %s, error:%s)' % (currency, e), 'when': datetime.datetime.utcnow()})
            self.removeCurrencyService(currency)
        return peers
    
    def listaccounts(self, gethidden=False, getarchived=False):
        '''
        Get a list of accounts. This method also supports filtering, fetches address for each account etc.
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("gethidden=%s&getarchived=%s" % (gethidden, getarchived))
        try:
            cache_object = self.cache['accounts'].get(cache_hash, None)
            if ((datetime.datetime.now() - cache_object['when']).seconds) < self.caching_time:
                cached_accounts = self.cache['accounts'][cache_hash]['data']
                return cached_accounts
        except:
            pass
        
        # get data from the connector (coind)
        fresh_accounts = {}
        for currency in self.config.keys():
            if self.config[currency]['enabled'] is True:
                try:
                    fresh_accounts[currency] = self.services[currency].listaccounts()
                except Exception, e:
                    # in case of an error, store the error, remove the service and move on
                    self.errors.append({'message': 'Error occurred while getting a list of accounts (currency: %s, error:%s)' % (currency, e), 'when': datetime.datetime.utcnow()})
                    self.removeCurrencyService(currency)
            
        # get a list of archived address
        address_ignore_list = []
        if not getarchived:
            ignore_list = accountFilter.objects.filter(status=1)
            for ignored_account in ignore_list:
                address_ignore_list.append(ignored_account.address.encode('ascii'))
        
        # get a list of hidden accounts
        address_hidden_list = []
        if not gethidden:
            hidden_list = accountFilter.objects.filter(status=2)
            for hidden_account in hidden_list:
                address_hidden_list.append(hidden_account.address.encode('ascii'))
        
        try:
            accounts = {}
            for currency in self.config.keys():
                if self.config[currency]['enabled'] is True:
                    accounts[currency] = []
                    if fresh_accounts.get(currency, False):
                        accounts_for_currency = fresh_accounts[currency]
            
                        for account_name, account_balance in accounts_for_currency.items():
                            try:
                                account_addresses = self.getaddressesbyaccount(account_name, currency)
                            except Exception, e:
                                self.errors.append({'message': 'Error getting addresses for account %s (currency: %s, error:%s)' % (account_name, currency, e), 'when': datetime.datetime.utcnow()})
                                
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
            self.errors.append({'message': 'Error occurred while compiling list of accounts (currency: %s, error:%s)' % (currency, e), 'when': datetime.datetime.utcnow()})
            self.removeCurrencyService(currency)
        
        # cache the result
        self.cache['accounts'][cache_hash] = {'data': accounts, 'when': datetime.datetime.now()}

        return accounts
    
    def getParamHash(self, param=""):
        '''
        This function takes a string and calculates a sha224 hash out of it. 
        It is used to hash the input parameters of functions/method in order to uniquely identify a cached result based only
        on the input parameters of the function/method call.
        '''
        cache_hash = hashlib.sha224(param).hexdigest()
        return cache_hash
    
    def getaddressesbyaccount(self, name, currency):
        '''
        Get the address of an account name
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("name=%s&currency=%s" % (name, currency))
        try:
            cache_object = self.cache['addressesbyaccount'].get(cache_hash, None)
            if ((datetime.datetime.now() - cache_object['when']).seconds) < self.caching_time:
                cached_addresses_by_account = self.cache['transactions'][cache_hash]['data']
                return cached_addresses_by_account
        except:
            pass
        
        if self.config.get(currency, False) and self.config[currency]['enabled'] is True:
            addresses = self.services[currency].getaddressesbyaccount(name)
            addresses_list = []
            for address in addresses:
                addresses_list.append(address.encode('ascii','ignore'))
        else:
            addresses_list = []
            
        # cache the result
        self.cache['addressesbyaccount'][cache_hash] = {'data': addresses_list, 'when': datetime.datetime.now()}
            
        return addresses_list
    
    def listtransactionsbyaccount(self, account_name, currency, limit=100000, start=0):    
        '''
        Get a list of transactions by account and currency
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("account_name=%s&currency=%s" % (account_name, currency))
        try:
            cache_object = self.cache['transactions'].get(cache_hash, None)
            if ((datetime.datetime.now() - cache_object['when']).seconds) < self.caching_time:
                cached_transactions = self.cache['transactions'][cache_hash]['data']
                return cached_transactions
        except:
            pass
        
        transactions = []
        if self.config[currency]['enabled'] is True:
            try:
                transactions = self.services[currency].listtransactions(account_name, limit, start)
            except Exception as e:
                self.errors.append({'message': 'Error occurred while compiling list of transactions (%s) while doing listtransactions()' % (e), 'when': datetime.datetime.utcnow()})
                self.removeCurrencyService(currency)
            
        for transaction in transactions:
            transaction['timereceived_pretty'] = generic.twitterizeDate(transaction.get('timereceived', 'never'))
            transaction['time_pretty'] = generic.twitterizeDate(transaction.get('time', 'never'))
            transaction['timereceived_human'] = datetime.datetime.fromtimestamp(transaction.get('timereceived', 0))
            transaction['time_human'] = datetime.datetime.fromtimestamp(transaction.get('time', 0))
            transaction['currency'] = currency
            transaction['details'] = {}
            if transaction.get('txid', False):
                transaction_details = self.gettransactiondetails(transaction, currency)
                if not transaction_details.get('code', False):
                    transaction['details'] = transaction_details
                else:
                    self.errors.append({'message': transaction_details, 'when': datetime.datetime.utcnow()})
            
        # cache the result
        self.cache['transactions'][cache_hash] = {'data': transactions, 'when': datetime.datetime.now()}

        return transactions
    
    def listtransactions(self, limit=100000, start=0):
        '''
        Get a list of transactions, default is 100000 transactions per account
        '''
        
        accounts = self.listaccounts(gethidden=True, getarchived=True)

        transactions = {}
        for currency in accounts.keys():
            transactions[currency] = []
            for account in accounts[currency]:
                # append list
                transactions[currency] = transactions[currency] + self.listtransactionsbyaccount(account['name'], currency, limit, start)

        return transactions
    
    def getnewaddress(self, currency, account_name):
        '''
        Create a new address
        '''
        new_address = None
        
        if currency not in self.config.keys():
            return False
        
        if self.config[currency]['enabled'] is True:
            if self.services.get(currency, False) and type(account_name) in [str, unicode] and len(account_name):
                new_address = self.services[currency].getnewaddress(account_name)
        else:
            return False
        
        return new_address
    
    def getbalance(self):
        '''
        Get balance for each currency
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("" % ())
        try:
            cache_object = self.cache['balances'].get(cache_hash, None)
            if ((datetime.datetime.now() - cache_object['when']).seconds) < self.caching_time:
                cached_balances = self.cache['balances'][cache_hash]['data']
                return cached_balances
        except:
            pass
        
        balances = {}
        for currency in self.config.keys():
            if self.config[currency]['enabled'] is True:
                try:
                    balances[currency] = generic.longNumber(self.services[currency].getbalance())
                except Exception as e:
                    # in case of an Exception continue on to the next currency service (xxxcoind)
                    self.errors.append({'message': 'Error occurred while getting balances (currency: %s, error: %s)' % (currency, e), 'when': datetime.datetime.utcnow()})
                    self.removeCurrencyService(currency)
        
        self.cache['balances'][cache_hash] = {'data': balances, 'when': datetime.datetime.now()}
        
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
            return {'message': 'Invalid input data from/to account name', 'code':-101}
        
        if currency not in self.services.keys():
            return {'message': 'Non-existing currency %s' % currency, 'code':-100}
        
        if self.config[currency]['enabled'] is not True:
            return {'message': 'Currency service %s disabled for now' % currency, 'code':-150}
        
        if not generic.isFloat(amount) or type(amount) is bool:
            return {'message': 'Amount is not a number', 'code':-102}
        
        if type(comment) not in [str, unicode]:
            return {'message': 'Comment is not valid', 'code':-104}
        
        try:
            minconf = int(minconf)
        except:
            return {'message': 'Invalid minconf value', 'code':-105}
        
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
            return {'message': 'source or destication account not found', 'code':-103}
              
    def sendfrom(self, from_account, to_address, amount, currency, minconf=1, comment="", comment_to=""):
        if not from_account or not to_address or not currency:
            return {'message': 'Invalid input data from account or address', 'code':-101}
        
        if currency not in self.services.keys():
            return {'message': 'Non-existing currency %s' % currency, 'code': -100}
        
        if not generic.isFloat(amount) or type(amount) is bool:
            return {'message': 'Amount is not a number', 'code':-102}

        if type(comment) not in [str, unicode]  or type(comment_to) not in [str, unicode]:
            return {'message': 'Comment is not valid', 'code':-104}
        
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
            except Exception, e: 
                return e.error
            
            return reply
        else:
            # account not found
            return {'message': 'Source account not found', 'code': -106}

    def gettransactiondetails(self, transaction, currency):
        '''
        Return transaction details
        '''
        if type(transaction) is not dict:
            return {'message': 'Invalid transaction details', 'code': -120}
        
        if currency not in self.config.keys():
            return {'message': 'Non-existing currency %s' % currency, 'code': -121}
        
        if self.config[currency]['enabled'] is not True:
            return {'message': 'Currency service %s disabled for now' % currency, 'code':-150}
        
        txid = transaction.get('txid', "")
        
        if type(txid) not in [str, unicode] or not len(txid):
            return {'message': 'Transaction ID is not valid', 'code': -127} 
        
        transaction_details = None
        try:
            transaction_details = self.services[currency].getrawtransaction(txid, 1)
        except JSONRPCException, e:
            return {}
        except Exception, e:
            return {}

        if transaction['category'] == 'receive':
            sender_address = self.decodeScriptSig(transaction_details, currency, self.getNet(currency))
        else:
            sender_address = ""
        
        return {'sender_address': sender_address}
        
    def decodeScriptSig(self, rawtransaction, currency, net='testnet'):
        '''
        Decode input script signature, courtesy of:
        http://bitcoin.stackexchange.com/questions/7838/why-does-gettransaction-report-me-only-the-receiving-address/8864#8864
        '''
        try:
            import base58
        except:
            return "need base58"
        
        try:
            script_sig = rawtransaction['vin'][0]['scriptSig']['asm']
        except:
            return "not enough info"
        
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
    
    def walletpassphrase(self, passphrase, currency):
        '''
        Unlock the wallet
        '''

        if type(passphrase) not in [str, unicode]:
            return {'message': 'Incorrect data type for passphrase', 'code': -110}
        
        if len(passphrase) < 1:
            return {'message': 'Incorrect data type for passphrase', 'code': -111}
        
        if currency not in self.services.keys():
            return {'message': 'Invalid non-existing or disabled currency', 'code': -112}
        
        if self.config[currency]['enabled'] is not True:
            return {'message': 'Currency service %s disabled for now' % currency, 'code':-150}
        
        try:
            unload_exit = self.services[currency].walletpassphrase(passphrase, 30)
        except JSONRPCException, e:
            return e.error
        except Exception, e:
            return e.error
         
        if type(unload_exit) is dict and unload_exit.get('code', None) and unload_exit['code'] < 0:
            # error occurred
            return unload_exit
        else:
            return True
        
    def walletlock(self, currency):
        '''
        Lock wallet
        '''
        if currency not in self.services.keys():
            return {'message': 'Invalid non-existing or disabled currency', 'code': -112}
        
        self.services[currency].walletlock()
        
        
