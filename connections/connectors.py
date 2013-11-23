import datetime
import generic
import hashlib
import events
from coinaddress import CoinAddress
from jsonrpc import ServiceProxy
from connections.cacher import Cacher 
from accounts.models import accountFilter
from bitcoinrpc.authproxy import JSONRPCException
from django.utils.timezone import utc

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
        self.cache = Cacher({
             'accounts': {},
             'transactions': {},
             'balances': {},
             'addressesbyaccount': {},
             })
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
                                                                            
    def getNet(self, provider_id):
        return self.config[provider_id].get('network', 'testnet')

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
    
    def getpeerinfo(self, provider_id):
        # get data from the connector (coind)
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
        return peers
    
    def listaccounts(self, gethidden=False, getarchived=False):
        '''
        Get a list of accounts. This method also supports filtering, fetches address for each account etc.
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("gethidden=%s&getarchived=%s" % (gethidden, getarchived))
        try:
            cache_object = self.cache['accounts'].get(cache_hash, None)
            if ((datetime.datetime.utcnow().replace(tzinfo=utc) - cache_object['when']).seconds) < self.caching_time:
                cached_accounts = self.cache['accounts'][cache_hash]['data']
                return cached_accounts
        except:
            pass
        
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
                                alternative_name = '(no name)'
                            else:
                                alternative_name = account_name
                            
                            # if there any address left then add it to the list
                            if account_addresses:
                                accounts[provider_id].append({
                                                           'name': account_name, 
                                                           'balance': self.longNumber(account_balance), 
                                                           'addresses': account_addresses, 
                                                           'hidden': hidden_flag,
                                                           'alternative_name': alternative_name,
                                                           'currency': self.config[provider_id]['currency'],
                                                           })
                    
        except Exception as e:
            self.errors.append({'message': 'Error occurred while compiling list of accounts (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
            self.removeCurrencyService(provider_id)
        
        # cache the result
        self.cache['accounts'][cache_hash] = {'data': accounts, 'when': datetime.datetime.utcnow().replace(tzinfo=utc)}

        return accounts
    
    def getParamHash(self, param=""):
        '''
        This function takes a string and calculates a sha224 hash out of it. 
        It is used to hash the input parameters of functions/method in order to 
        uniquely identify a cached result based  only on the input parameters of 
        the function/method call.
        '''
        cache_hash = hashlib.sha224(param).hexdigest()
        return cache_hash
    
    def getaddressesbyaccount(self, name, provider_id):
        '''
        Get the address of an account name
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("name=%s&provider_id=%s" % (name, provider_id))
        try:
            cache_object = self.cache['addressesbyaccount'].get(cache_hash, None)
            if ((datetime.datetime.utcnow().replace(tzinfo=utc) - cache_object['when']).seconds) < self.caching_time:
                cached_addresses_by_account = self.cache['transactions'][cache_hash]['data']
                return cached_addresses_by_account
        except:
            pass
        
        if self.config.get(provider_id, False) and self.config[provider_id]['enabled'] is True:
            addresses = self.services[provider_id].getaddressesbyaccount(name)
            addresses_list = []
            for address in addresses:
                coinaddr = CoinAddress(address)
                addresses_list.append(coinaddr)
        else:
            addresses_list = []
            
        # cache the result
        self.cache['addressesbyaccount'][cache_hash] = {'data': addresses_list, 'when': datetime.datetime.utcnow().replace(tzinfo=utc)}
            
        return addresses_list
    
    def listtransactionsbyaccount(self, account_name, provider_id, limit=100000, start=0):    
        '''
        Get a list of transactions by account name and provider_id
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("account_name=%s&provider_id=%s" % (account_name, provider_id))
        try:
            cache_object = self.cache['transactions'].get(cache_hash, None)
            if ((datetime.datetime.utcnow().replace(tzinfo=utc) - cache_object['when']).seconds) < self.caching_time:
                cached_transactions = self.cache['transactions'][cache_hash]['data']
                return cached_transactions
        except:
            pass
        
        transactions = []
        if self.config[provider_id]['enabled'] is True:
            try:
                transactions = self.services[provider_id].listtransactions(account_name, limit, start)
            except Exception as e:
                self.errors.append({'message': 'Error occurred while compiling list of transactions (%s) while doing listtransactions()' % (e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                self.removeCurrencyService(provider_id)
            
        for transaction in transactions:
            if transaction.get('address', False):
                transaction['address'] = CoinAddress(transaction['address'])
            
            transaction['provider_id'] = provider_id
            transaction['timereceived_pretty'] = generic.twitterizeDate(transaction.get('timereceived', 'never'))
            transaction['time_pretty'] = generic.twitterizeDate(transaction.get('time', 'never'))
            transaction['timereceived_human'] = datetime.datetime.fromtimestamp(transaction.get('timereceived', 0))
            transaction['time_human'] = datetime.datetime.fromtimestamp(transaction.get('time', 0))
            transaction['currency'] = self.config[provider_id]['currency']
            
            transaction['details'] = {}
            if transaction.get('txid', False):
                transaction_details = self.gettransactiondetails(transaction, provider_id)
                if not transaction_details.get('code', False):
                    transaction['details'] = transaction_details
                else:
                    self.errors.append({'message': transaction_details, 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
            
        # cache the result
        self.cache['transactions'][cache_hash] = {'data': transactions, 'when': datetime.datetime.utcnow().replace(tzinfo=utc)}

        return transactions
    
    def listtransactions(self, limit=100000, start=0):
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
    
    def getbalance(self):
        '''
        Get balance for each currency
        '''
        
        # check for cached data, use that or get it again
        cache_hash = self.getParamHash("" % ())
        try:
            cache_object = self.cache['balances'].get(cache_hash, None)
            if ((datetime.datetime.utcnow().replace(tzinfo=utc) - cache_object['when']).seconds) < self.caching_time:
                cached_balances = self.cache['balances'][cache_hash]['data']
                return cached_balances
        except:
            pass
        
        balances = {}
        for provider_id in self.config.keys():
            if self.config[provider_id]['enabled'] is True:
                try:
                    balances[provider_id] = generic.longNumber(self.services[provider_id].getbalance())
                except Exception as e:
                    # in case of an Exception continue on to the next currency service (xxxcoind)
                    self.errors.append({'message': 'Error occurred while getting balances (provider id: %s, error: %s)' % (provider_id, e), 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
                    self.removeCurrencyService(provider_id)
        
        self.cache['balances'][cache_hash] = {'data': balances, 'when': datetime.datetime.utcnow().replace(tzinfo=utc)}
        
        return balances
    
    def getaccountdetailsbyaddress(self, address):
        '''
        Return account details 
        '''
        
        accounts = self.listaccounts(gethidden=True, getarchived=True)
        
        target_account = None
        for provider_id in accounts.keys():
            for account in accounts[provider_id]:
                if address in account['addresses']:
                    target_account = account
                    target_account['currency'] = self.config[provider_id]['currency']
                    target_account['provider_id'] = provider_id
                    break
        return target_account

    def moveamount(self, from_account, to_account, provider_id, amount, minconf=1, comment=""):
        if not from_account or not to_account or not provider_id:
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
            return {'message': 'source or destication account not found', 'code':-103}
              
    def sendfrom(self, from_account, to_address, amount, provider_id, minconf=1, comment="", comment_to=""):
        if not from_account or not to_address or not provider_id:
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
        except JSONRPCException, e:
            return {}
        except Exception, e:
            return {}

        if transaction['category'] == 'receive':
            sender_address = self.decodeScriptSig(transaction_details, self.config[provider_id]['currency'], self.getNet(provider_id))
        else:
            sender_address = ""
        
        return {'sender_address': sender_address}
    
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
        except JSONRPCException, e:
            return {}
        except Exception, e:
            return {}
    
        return transaction_details

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
        
        return encoded_address
    
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
        
    def walletlock(self, provider_id):
        '''
        Lock wallet
        '''
        if provider_id not in self.services.keys():
            return {'message': 'Invalid non-existing or disabled currency', 'code': -112}
        
        self.services[provider_id].walletlock()
        
