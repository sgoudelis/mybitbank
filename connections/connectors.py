import datetime
import generic
import hashlib
import events
import time
from coinaddress import CoinAddress
from coinaccount import CoinAccount
from cointransaction import CoinTransaction
#from bitcoinrpc.authproxy import AuthServiceProxy
from jsonrpc import ServiceProxy
from connections.cacher import Cacher 
from accounts.models import accountFilter
from bitcoinrpc.authproxy import JSONRPCException
from django.utils.timezone import utc

measure_time = False

def timeit(method):
    if measure_time is not True:
        return method
    
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r() (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts)
        return result

    return timed

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
    cache = Cacher({
             'accounts': {},
             'transactions': {},
             'balances': {},
             'addressesbyaccount': {},
             'info': {},
             })
    
    @timeit
    def __init__(self):
        '''
        Constructor, load config 
        '''
        self.cache.setDebug(False)
        try:
            import config
            currency_configs = config.config
        except (AttributeError, ImportError) as e:
            self.errors.append({'message': 'Error occurred while compiling list of accounts (%s)' % (e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})

        for currency_config in currency_configs:
            # true is enabled, anything but boolean is disabled up to the value as a timestamp
            # this will caught by the middleware
            
            self.config[currency_config['id']] = currency_config
            self.config[currency_config['id']]['enabled'] = True
            self.services[currency_config['id']] = ServiceProxy("http://%s:%s@%s:%s" % 
                                                                             (currency_config['rpcusername'], 
                                                                              currency_config['rpcpassword'], 
                                                                              currency_config['rpchost'], 
                                                                              currency_config['rpcport']))
            
            '''
            self.services[currency_config['id']] = AuthServiceProxy("http://%s:%s@%s:%s" % 
                                                                 (currency_config['rpcusername'], 
                                                                  currency_config['rpcpassword'], 
                                                                  currency_config['rpchost'], 
                                                                  currency_config['rpcport']))
            '''
            
    @timeit
    def getNet(self, provider_id):
        '''
        Return network value, mainnet or testnet
        '''
        info = self.getinfo(provider_id)
        is_testnet = False
        if info.has_key('testnet'):
            is_testnet = info.get('testnet')
            if is_testnet is False:
                return "mainnet"
            elif is_testnet is True:
                return "testnet"
        else:
            # default to mainnet
            return "mainnet"
    
    @timeit
    def removeCurrencyService(self, provider_id):
        '''
        Remove the ServiceProxy object from the list of service in case of a xxxcoind daemon not responding in time
        '''
        
        if self.config.get(provider_id, False):
            currency_provider_config = self.config.get(provider_id, {})
            self.alerts.append({'type': 'currencybackend', 'provider_id': provider_id, 'message': 'Currency service provider %s named %s is disabled for %s seconds due an error communicating.' % (provider_id, self.config[provider_id]['name'], self.disable_time), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
            self.config[provider_id]['enabled'] = datetime.datetime.utcnow().replace(tzinfo=utc) + datetime.timedelta(0,self.disable_time)
            events.addEvent(None, "Currency service %s has being disabled for %s seconds" % (currency_provider_config['currency'], self.disable_time), 'alert')
            del self.services[provider_id]

    def longNumber(self, x):
        '''
        Convert number coming from the JSON-RPC to a human readable format with 8 decimal
        '''
        return "{:.8f}".format(x)
    
    @timeit
    def getinfo(self, provider_id):
        '''
        Get xxxcoind info
        '''
        
        if provider_id not in self.services.keys():
            return {'message': 'Non-existing currency provider id %s' % provider_id, 'code':-100}
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("provider_id=%s" % provider_id)
        cached_peerinfo = self.cache.fetch('info', cache_hash)
        if cached_peerinfo:
            return cached_peerinfo
        
        peerinfo = {}
        try:        
            peerinfo = self.services[provider_id].getinfo()
        except (JSONRPCException, Exception), e:
            self.errors.append({'message': 'Error occurred while getting info from currency provider (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
            self.removeCurrencyService(provider_id)
        
        self.cache.store('info', cache_hash, peerinfo)
        
        return peerinfo
    
    @timeit
    def getpeerinfo(self, provider_id):
        '''
        Get peer info from the connector (xxxcoind)
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("provider_id=%s" % provider_id)
        cached_peerinfo = self.cache.fetch('peerinfo', cache_hash)
        if cached_peerinfo:
            return cached_peerinfo
        
        peers = []
        try:
            if self.config[provider_id]['enabled'] is True:
                peers = self.services[provider_id].getpeerinfo()
        except JSONRPCException:
            # in case coind not support getpeerinfo command
            return {'error'} 
        except Exception, e:
            # in case of an error, store the error, disabled the service and move on
            self.errors.append({'message': 'Error occurred while getting peers info of accounts (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
            self.removeCurrencyService(provider_id)
            
        # cache peer info
        self.cache.store('peerinfo', cache_hash, peers)
        
        return peers
    
    @timeit
    def listaccounts(self, gethidden=False, getarchived=False):
        '''
        Get a list of accounts. This method also supports filtering, fetches address for each account etc.
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("gethidden=%s&getarchived=%s" % (gethidden, getarchived))
        cached_object = self.cache.fetch('accounts', cache_hash)
        if cached_object:
            return cached_object
        
        # get data from the connector (coind)
        fresh_accounts = {}
        for provider_id in self.config.keys():
            if self.config[provider_id]['enabled'] is True:
                try:
                    fresh_accounts[provider_id] = self.services[provider_id].listaccounts()
                except Exception, e:
                    # in case of an error, store the error, remove the service and move on
                    self.errors.append({'message': 'Error occurred while getting a list of accounts (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                    self.removeCurrencyService(provider_id)
            
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
            for provider_id in self.config.keys():
                if self.config[provider_id]['enabled'] is True:
                    accounts[provider_id] = []
                    if fresh_accounts.get(provider_id, False):
                        accounts_for_currency = fresh_accounts[provider_id]
            
                        for account_name, account_balance in accounts_for_currency.items():
                            try:
                                account_addresses = self.getaddressesbyaccount(account_name, provider_id)
                            except Exception, e:
                                self.errors.append({'message': 'Error getting addresses for account %s (provider id: %s, error: %s)' % (account_name, provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                                
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
                                alternative_name = '(default account)'
                            else:
                                alternative_name = account_name
                            
                            # if there any address left then add it to the list
                            if account_addresses:
                                accounts[provider_id].append(CoinAccount({
                                                           'name': account_name, 
                                                           'balance': self.longNumber(account_balance), 
                                                           'addresses': account_addresses, 
                                                           'hidden': hidden_flag,
                                                           'alternative_name': alternative_name,
                                                           'currency': self.config[provider_id]['currency'],
                                                           'provider_id': provider_id,
                                                           }))
                    
        except Exception as e:
            self.errors.append({'message': 'Error occurred while compiling list of accounts (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
            self.removeCurrencyService(provider_id)
        
        # cache the result
        self.cache.store('accounts', cache_hash, accounts)
        return accounts
    
    @timeit
    def getParamHash(self, param=""):
        '''
        This function takes a string and calculates a sha224 hash out of it. 
        It is used to hash the input parameters of functions/method in order to 
        uniquely identify a cached result based  only on the input parameters of 
        the function/method call.
        '''
        cache_hash = hashlib.sha224(param).hexdigest()
        return cache_hash
    
    @timeit
    def getaddressesbyaccount(self, name, provider_id):
        '''
        Get the address of an account name
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("name=%s&provider_id=%s" % (name, provider_id))
        cached_object = self.cache.fetch('addressesbyaccount', cache_hash)
        if cached_object:
            return cached_object
        
        if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
            try:
                addresses = self.services[provider_id].getaddressesbyaccount(name)
            except Exception, e:
                self.errors.append({'message': 'Error occurred while compiling a list of addresses (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                self.removeCurrencyService(provider_id)
            
            addresses_list = []
            for address in addresses:
                coinaddr = CoinAddress(address)
                addresses_list.append(coinaddr)
        else:
            addresses_list = []
            
        # cache the result
        self.cache.store('addressesbyaccount', cache_hash, addresses_list)
        return addresses_list
    
    @timeit
    def listtransactionsbyaccount(self, account_name, provider_id, limit=100000, start=0):    
        '''
        Get a list of transactions by account name and provider_id
        '''
        
        cache_hash = self.getParamHash("account_name=%s&provider_id=%s&limit=%s&start=%s" % (account_name, provider_id, limit, start))
        cached_object = self.cache.fetch('transactions', cache_hash)
        if cached_object:
            return cached_object
        
        transactions = []
        transaction_list = []
        if self.config[provider_id]['enabled'] is True:
            try:
                transaction_list = self.services[provider_id].listtransactions(account_name, limit, start)
            except Exception as e:
                self.errors.append({'message': 'Error occurred while compiling list of transactions (%s) while doing listalltransactions()' % (e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                self.removeCurrencyService(provider_id)
            
        for entry in transaction_list:
            if entry.get('address', False):
                entry['address'] = CoinAddress(entry['address'])
            
            entry['provider_id'] = provider_id
            entry['timereceived_pretty'] = generic.twitterizeDate(entry.get('timereceived', 'never'))
            entry['time_pretty'] = generic.twitterizeDate(entry.get('time', 'never'))
            entry['timereceived_human'] = datetime.datetime.fromtimestamp(entry.get('timereceived', 0))
            entry['time_human'] = datetime.datetime.fromtimestamp(entry.get('time', 0))
            entry['currency'] = self.config[provider_id]['currency']
            
            entry['details'] = {}
            if entry.get('txid', False):
                transaction_details = self.gettransactiondetails(entry, provider_id)
                if not transaction_details.get('code', False):
                    entry['details'] = transaction_details
                else:
                    self.errors.append({'message': transaction_details, 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
            transactions.append(CoinTransaction(entry))
            
        # cache the result
        self.cache.store('transactions', cache_hash, transactions)
        return transactions
    
    @timeit
    def listalltransactions(self, limit=100000, start=0):
        '''
        Get a list of transactions, default is 100000 transactions per account
        '''
        
        accounts = self.listaccounts(gethidden=True, getarchived=True)
        transactions = {}
        for provider_id in accounts.keys():
            transactions[provider_id] = []
            for account in accounts[provider_id]:
                # append list
                transactions[provider_id] = transactions[provider_id] + self.listtransactionsbyaccount(account['name'], provider_id, limit, start)

        return transactions
    
    @timeit
    def getnewaddress(self, provider_id, account_name):
        '''
        Create a new address
        '''
        new_address = None
        
        if provider_id not in self.config.keys():
            return False
        
        if self.config[provider_id]['enabled'] is True:
            if self.services.get(provider_id, False) and type(account_name) in [str, unicode] and len(account_name):
                new_address = self.services[provider_id].getnewaddress(account_name)
                # clear cache
                self.cache['accounts'] = {}
                return new_address
        else:
            return False
        
        return new_address
    
    @timeit
    def getbalance(self):
        '''
        Get balance for each currency
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("" % ())
        cached_object = self.cache.fetch('balances', cache_hash)
        if cached_object:
            return cached_object
        
        balances = {}
        for provider_id in self.config.keys():
            if self.config[provider_id]['enabled'] is True:
                try:
                    balances[provider_id] = generic.longNumber(self.services[provider_id].getbalance())
                except Exception as e:
                    # in case of an Exception continue on to the next currency service (xxxcoind)
                    self.errors.append({'message': 'Error occurred while getting balances (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                    self.removeCurrencyService(provider_id)
        
        # store data to cache
        self.cache.store('balances', cache_hash, balances)
        
        return balances
    
    @timeit
    def getaccountdetailsbyaddress(self, address, filter_provider_id=False):
        '''
        Return account details by address
        '''
        
        accounts = self.listaccounts(gethidden=True, getarchived=True)
        
        if filter_provider_id is not False:
            provider_ids = [filter_provider_id]
        else:
            provider_ids = accounts.keys()
        
        provider_ids = map(int, provider_ids)
        
        target_account = None
        for provider_id in provider_ids:
            for account in accounts[provider_id]:
                if address in account['addresses']:
                    target_account = account
                    target_account['currency'] = self.config[provider_id]['currency']
                    target_account['provider_id'] = provider_id
                    break
        return target_account
   
    @timeit
    def getdefaultaccount(self, provider_id):
        '''
        Return the default (default account) account for a provider
        '''
        
        account_addresses = self.getaddressesbyaccount(u'', provider_id)
        account = self.getaccountdetailsbyaddress(account_addresses[0])
        return account
    
    @timeit
    def moveamount(self, from_account, to_account, provider_id, amount, minconf=1, comment=""):
        '''
        Move amount from local to local accounts
        Note: from_account my be an empty string 
        '''
        if not to_account or not provider_id:
            return {'message': 'Invalid input data from/to account name', 'code':-101}
        
        if provider_id not in self.services.keys():
            return {'message': 'Non-existing currency provider id %s' % provider_id, 'code':-100}
        
        if self.config[provider_id]['enabled'] is not True:
            return {'message': 'Currency service with id %s disabled for now' % provider_id, 'code':-150}
        
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
        for account in account_list[provider_id]:
            account_names.append(account['name'])
        
        if from_account in account_names and to_account in account_names:
            # both accounts have being found, perform the move
            try:
                reply = self.services[provider_id].move(from_account, to_account, amount, minconf, comment)
            except JSONRPCException, e: 
                return e.error
            except ValueError, e:
                return {'message': e, 'code':-1}
            
            return reply
        else:
            # account not found
            return {'message': 'source or destination account not found', 'code':-103}
    
    @timeit          
    def sendfrom(self, from_account, to_address, amount, provider_id, minconf=1, comment="", comment_to=""):
        print "%s %s %s" % (from_account, to_address, provider_id)
        if not to_address or not provider_id:
            return {'message': 'Invalid input data from account or address', 'code':-101}

        if provider_id not in self.services.keys():
            return {'message': 'Non-existing currency provider id %s' % provider_id, 'code': -100}
        
        if not generic.isFloat(amount) or type(amount) is bool:
            return {'message': 'Amount is not a number', 'code':-102}

        if type(comment) not in [str, unicode]  or type(comment_to) not in [str, unicode]:
            return {'message': 'Comment is not valid', 'code':-104}
        
        account_list = self.listaccounts(True, True)
        
        account_names = []
        for account in account_list[provider_id]:
            account_names.append(account['name'])
            
        if from_account in account_names:
            # account given exists, continue
            try:
                reply = self.services[provider_id].sendfrom(from_account, to_address, amount, minconf, comment, comment_to)
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

    @timeit
    def gettransactiondetails(self, transaction, provider_id):
        '''
        Return transaction details, like sender address
        '''
        if type(transaction) is not dict:
            return {'message': 'Invalid transaction details', 'code': -120}
        
        if provider_id not in self.config.keys():
            return {'message': 'Non-existing currency provider id %s' % provider_id, 'code': -121}
        
        if self.config[provider_id]['enabled'] is not True:
            return {'message': 'Currency service %s disabled for now' % provider_id, 'code':-150}
        
        txid = transaction.get('txid', "")
        
        if type(txid) not in [str, unicode] or not len(txid):
            return {'message': 'Transaction ID is not valid', 'code': -127} 
        
        transaction_details = None
        try:
            transaction_details = self.services[provider_id].getrawtransaction(txid, 1)
        except JSONRPCException:
            return {}
        except Exception:
            return {}

        if transaction['category'] == 'receive':
            sender_address = self.decodeScriptSig(transaction_details, self.config[provider_id]['currency'], self.getNet(provider_id))
        else:
            sender_address = ""
            
        return {'sender_address': sender_address}
    
    @timeit
    def decoderawtransaction(self, transaction, provider_id):
        return self.services[provider_id].decoderawtransaction(transaction)
    
    @timeit
    def gettransaction(self, txid, provider_id):
        '''
        Return transaction
        '''
        if provider_id not in self.config.keys():
            return {'message': 'Non-existing currency provider id %s' % provider_id, 'code': -121}
        
        if self.config[provider_id]['enabled'] is not True:
            return {'message': 'Currency service provider id %s disabled for now' % provider_id, 'code':-150}
        
        if type(txid) not in [str, unicode] or not len(txid):
            return {'message': 'Transaction ID is not valid', 'code': -127} 
        
        transaction_details = None
        try:
            transaction_details = self.services[provider_id].gettransaction(txid)
        except JSONRPCException:
            return {}
        except Exception:
            return {}
    
        return CoinTransaction(transaction_details)

    @timeit
    def decodeScriptSig(self, rawtransaction, currency, net='testnet'):
        '''
        Decode input script signature, courtesy of:
        http://bitcoin.stackexchange.com/questions/7838/why-does-gettransaction-report-me-only-the-receiving-address/8864#8864
        '''
        
        try:
            script_sig = rawtransaction['vin'][0]['scriptSig']['asm']
        except:
            return "not enough info"
        
        script = script_sig.split()
        
        h = hashlib.sha256(script[1].decode("hex")).digest()
        ripe160 =  hashlib.new('ripemd160')
        ripe160.update(h)
        d = ripe160.digest()
        
        prefix = self.prefixes[currency.lower()][net]
        address = (prefix + d)
        
        # calculate checksum
        checksum = hashlib.sha256(hashlib.sha256(address).digest()).digest()[:4]
        
        # build the raw address
        address += checksum
        
        # encode the address in base58
        encoded_address = generic.b58encode(address)
        
        return encoded_address
    
    @timeit
    def walletpassphrase(self, passphrase, provider_id):
        '''
        Unlock the wallet
        '''

        if type(passphrase) not in [str, unicode]:
            return {'message': 'Incorrect data type for passphrase', 'code': -110}
        
        if len(passphrase) < 1:
            return {'message': 'Incorrect data type for passphrase', 'code': -111}
        
        if provider_id not in self.services.keys():
            return {'message': 'Invalid non-existing or disabled currency', 'code': -112}
        
        if self.config[provider_id]['enabled'] is not True:
            return {'message': 'Currency service provider id %s disabled for now' % provider_id, 'code':-150}
        
        try:
            unload_exit = self.services[provider_id].walletpassphrase(passphrase, 30)
        except JSONRPCException, e:
            return e.error
        except Exception, e:
            return e.error
         
        if type(unload_exit) is dict and unload_exit.get('code', None) and unload_exit['code'] < 0:
            # error occurred
            return unload_exit
        else:
            return True
    
    @timeit    
    def walletlock(self, provider_id):
        '''
        Lock wallet
        '''
        if provider_id not in self.services.keys():
            return {'message': 'Invalid non-existing or disabled currency', 'code': -112}
        
        self.services[provider_id].walletlock()
        
