import datetime
import generic
import hashlib
import events
import time
import copy
from coinaccount import CoinAccount
#from bitcoinrpc.authproxy import AuthServiceProxy
from jsonrpc import ServiceProxy
from connections.cacher import Cacher 
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
                'doge': {'mainnet': '\x30', 'testnet': '\x6f'},
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
            import walletconfig
            currency_configs = walletconfig.config
        except (AttributeError, ImportError) as e:
            self.errors.append({'message': 'Error occurred while loading the wallet configuration file (%s)' % (e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})

        for currency_config in currency_configs:
            if currency_config.get('enabled', True):
                self.config[currency_config['id']] = currency_config
                self.config[currency_config['id']]['enabled'] = True
                self.services[currency_config['id']] = ServiceProxy("http://%s:%s@%s:%s" % 
                                                         (currency_config['rpcusername'], 
                                                          currency_config['rpcpassword'], 
                                                          currency_config['rpchost'], 
                                                          currency_config['rpcport']))

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
            if currency_provider_config.get('enabled', False) is True:
                self.alerts.append({'type': 'currencybackend', 'provider_id': provider_id, 'message': 'Currency service provider %s named %s is disabled for %s seconds due an error communicating.' % (provider_id, currency_provider_config['name'], self.disable_time), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                currency_provider_config['enabled'] = datetime.datetime.utcnow().replace(tzinfo=utc) + datetime.timedelta(0,self.disable_time)
                currency_provider_config["pipes"] = datetime.datetime.utcnow().replace(tzinfo=utc) + datetime.timedelta(0,self.disable_time)
                events.addEvent(None, "Currency service %s has being disabled for %s seconds" % (currency_provider_config['currency'], self.disable_time), 'alert')
                if self.services.get(provider_id):
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
        
        peerinfo = {}
        try:
            if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
                peerinfo = self.services[provider_id].getinfo()
        except (JSONRPCException, Exception), e:
            self.errors.append({'message': 'Error occurred while doing getinfo (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
            self.removeCurrencyService(provider_id)
        
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
            if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
                peers = self.services[provider_id].getpeerinfo()
        except JSONRPCException:
            # in case coind not support getpeerinfo command
            return {'error'} 
        except Exception, e:
            # in case of an error, store the error, disabled the service and move on
            self.errors.append({'message': 'Error occurred while doing getpeerinfo (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
            self.removeCurrencyService(provider_id)
            
        # cache peer info
        self.cache.store('peerinfo', cache_hash, peers)
        
        return peers
    
    @timeit
    def listAccounts(self, gethidden=False, getarchived=False, selected_provider_id=-1):
        '''
        Get a list of accounts. This method also supports filtering, fetches address for each account etc.
        '''
        
        # get data from the connector (xxxcoind)
        fresh_accounts = {}
        
        if selected_provider_id > 0:
            provider_ids = [int(selected_provider_id)]
        else:
            provider_ids = self.config.keys()
        
        for provider_id in provider_ids:
            if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
                try:
                    fresh_accounts[provider_id] = self.services[provider_id].listaccounts()
                    for fresh_account_name, fresh_account_balance in fresh_accounts[provider_id].items():
                        fresh_accounts[provider_id][fresh_account_name] = self.longNumber(fresh_account_balance)
                    
                except Exception, e:
                    # in case of an error, store the error, remove the service and move on
                    self.errors.append({'message': 'Error occurred while doing listaccounts (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                    self.removeCurrencyService(provider_id)
                    
        return fresh_accounts
        
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
    def getAddressesByAccount(self, account, provider_id):
        '''
        Get the address of an account name
        '''
        
        if type(account) in [str, unicode]:
            name = account
        elif isinstance(account, CoinAccount):
            name = account['name']
        else:
            return []
            
        addresses = []
        if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
            try:
                addresses = self.services[provider_id].getaddressesbyaccount(name)
            except Exception, e:
                self.errors.append({'message': 'Error occurred while doing getaddressesbyaccount (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                self.removeCurrencyService(provider_id)

        return addresses
    
    @timeit
    def listTransactionsByAccount(self, account_name, provider_id, limit=100000, start=0):    
        '''
        Get a list of transactions by account name and provider_id
        '''
        
        transactions = []
        if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
            try:
                transactions = self.services[provider_id].listtransactions(account_name, limit, start)
            except Exception as e:
                self.errors.append({'message': 'Error occurred while doing listtransactions (provider_id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                self.removeCurrencyService(provider_id)
            
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
        
        if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
            if self.services.get(provider_id, False) and type(account_name) in [str, unicode]:
                new_address = self.services[provider_id].getnewaddress(account_name)
                return new_address
        else:
            return False
    
    @timeit
    def getBalance(self, selected_provider_id=0, account_name="*"):
        '''
        Get balance for each provider
        '''
        balances = {}
        
        if selected_provider_id>0:
            provider_ids = [selected_provider_id]
        else:
            provider_ids = self.config.keys()
        
        for provider_id in provider_ids:
            if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
                try:
                    balances[provider_id] = generic.longNumber(self.services[provider_id].getbalance(account_name))
                except Exception as e:
                    # in case of an Exception continue on to the next currency service (xxxcoind)
                    self.errors.append({'message': 'Error occurred while doing getbalance (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                    self.removeCurrencyService(provider_id)
        
        return balances
   
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
        
        account_list = self.services[provider_id].listaccounts()

        account_names = []
        for account_name, account_balance in account_list.items():
            account_names.append(account_name)
        
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
        if type(from_account) not in [str, unicode]:
            return {'message': 'Invalid input from account', 'code':-156}
        
        if not to_address or not provider_id:
            return {'message': 'Invalid input to account or address', 'code':-101}

        if provider_id not in self.services.keys():
            return {'message': 'Non-existing currency provider id %s' % provider_id, 'code': -100}
        
        if not generic.isFloat(amount) or type(amount) is bool:
            return {'message': 'Amount is not a number', 'code':-102}

        if type(comment) not in [str, unicode]  or type(comment_to) not in [str, unicode]:
            return {'message': 'Comment is not valid', 'code':-104}
        
        account_list = self.services[provider_id].listaccounts()
        
        account_names = []
        for account_name, account_balance in account_list.items():
            account_names.append(account_name)
            
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
    def getRawTransaction(self, txid, provider_id):
        '''
        Return transaction details, like sender address
        '''

        if provider_id not in self.config.keys():
            return {'message': 'Non-existing currency provider id %s' % provider_id, 'code': -121}
        
        if self.config[provider_id]['enabled'] is not True:
            return {'message': 'Currency service %s disabled for now' % provider_id, 'code':-150}
        
        if type(txid) not in [str, unicode] or not len(txid):
            return {'message': 'Transaction ID is not valid', 'code': -127} 
        
        transaction_details = None
        try:
            if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
                transaction_details = self.services[provider_id].getrawtransaction(txid, 1)
        except JSONRPCException:
            return {}
        except Exception:
            return {}
        
        return transaction_details
    
    @timeit
    def decoderawtransaction(self, transaction, provider_id):
        '''
        Decode raw transaction
        '''
        if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
            return self.services[provider_id].decoderawtransaction(transaction)
    
    @timeit
    def getTransaction(self, txid, provider_id):
        '''
        Return a transaction
        '''
        if provider_id not in self.config.keys():
            return {'message': 'Non-existing currency provider id %s' % provider_id, 'code': -121}
        
        if self.config[provider_id]['enabled'] is not True:
            return {'message': 'Currency service provider id %s disabled for now' % provider_id, 'code':-150}
        
        if type(txid) not in [str, unicode] or not len(txid):
            return {'message': 'Transaction ID is not valid', 'code': -127} 
        
        transaction_details = None
        try:
            if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
                transaction_details = self.services[provider_id].gettransaction(txid)
        except JSONRPCException:
            return {}
        except Exception:
            return {}
    
        return transaction_details
    
    @timeit
    def walletpassphrase(self, passphrase, provider_id):
        '''
        Unlock the wallet
        '''

        if type(passphrase) not in [str, unicode]:
            return {'message': 'Incorrect data type for passphrase', 'code': -110}
        
        if len(passphrase) < 1:
            return {'message': 'No passphrase given', 'code': -111}
        
        if provider_id not in self.services.keys():
            return {'message': 'Invalid non-existing or disabled currency', 'code': -112}
        
        if self.config[provider_id]['enabled'] is not True:
            return {'message': 'Currency service provider id %s disabled for now' % provider_id, 'code':-150}
        
        try:
            if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
                unload_exit = self.services[provider_id].walletpassphrase(passphrase, 30)
            else:
                return False
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
        
        if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
            self.services[provider_id].walletlock()
        
