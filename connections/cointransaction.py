import connections
import generic
import config
import hashlib
import datetime
from connections.cacher import Cacher
from connections.coinaddress import CoinAddress

class CoinTransaction(object):
    '''
    Class for a transaction
    '''
    
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
    
    def __init__(self, transactionDetails):
        self._transaction = {}
        self. _cache = Cacher({
                     'details': {},
                     })
        
        if type(transactionDetails) is dict:
            self._transaction = transactionDetails
            
            self['timereceived_pretty'] = generic.twitterizeDate(self.get('timereceived', 'never'))
            self['time_pretty'] = generic.twitterizeDate(self.get('time', 'never'))
            self['timereceived_human'] = datetime.datetime.fromtimestamp(self.get('timereceived', 0))
            self['time_human'] = datetime.datetime.fromtimestamp(self.get('time', 0))
            self['blocktime_human'] = datetime.datetime.fromtimestamp(self.get('blocktime', 0))
            self['blocktime_pretty'] = generic.twitterizeDate(self.get('blocktime', 'never'))
            self['currency_symbol'] = generic.getCurrencySymbol(self['currency'])
            
            if self.get('category', False) in ['receive','send']:
                if self['confirmations'] <= config.MainConfig['globals']['confirmation_limit']:
                    self['status_icon'] = 'glyphicon-time'
                    self['status_color'] = '#AAA';
                    self['tooltip'] = self['confirmations']
                else:
                    self['status_icon'] = 'glyphicon-ok-circle'
                    self['status_color'] = '#1C9E3F';
                    self['tooltip'] = self['confirmations']
            
            accountObject = self['wallet'].getAccountByName(self['account'])
            self['account'] = accountObject
            
            if self['category'] == 'receive':
                self['icon'] = 'glyphicon-circle-arrow-down'
            elif self['category'] == 'send':
                self['icon'] = 'glyphicon-circle-arrow-up'
            elif self['category'] == 'move':
                self['icon'] = 'glyphicon-circle-arrow-right'
                self['otheraccount'] = self['wallet'].getAccountByName(self['otheraccount'])
            
    def __getitem__(self, key):
        '''
        Getter for dictionary-line behavior
        '''
        if key == "account":
            if self.haskey("account"):
                return self._transaction['account']
            else:
                return self._transaction['details'][0]['account']
        elif key == "category":
            if self.haskey("category"):
                return self._transaction['category']
            else:
                return self._transaction['details'][0]['category']
        elif key == "currency_symbol":
            return self.getCurrencySymbol()
        elif key == "currency_code":
            return self.getCurrencyCode()
        elif key == "raw_transaction":
            return self.getRawTransaction()
        elif key == "source_address":
            return self.getSenderAddress()
        
        transaction = getattr(self, '_transaction')
        return transaction.get(key, None)
     
    def __setitem__(self, key, value):
        '''
        Setter for dictionary-line behavior
        '''
        transaction = getattr(self, '_transaction')
        transaction[key] = value
        return setattr(self, '_transaction', transaction)
    
    def get(self, key, default=False):
        '''
        get() method for dictionary-line behavior
        '''
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
        
    @property
    def provider_id(self):
        '''
        Property for the provider id
        '''
        return self.get('provider_id', None)
    
    @property
    def transaction_id(self):
        '''
        Property for the txid
        '''
        return self.get('txid', None)
    
    @property
    def txid(self):
        '''
        Property for the txid
        '''
        return self.get('txid', None)
    
    def getParamHash(self, param=""):
        '''
        This function takes a string and calculates a sha224 hash out of it. 
        It is used to hash the input parameters of functions/method in order to 
        uniquely identify a cached result based  only on the input parameters of 
        the function/method call.
        '''
        cache_hash = hashlib.sha224(param).hexdigest()
        return cache_hash
    
    def metaProperties(self):
        '''
        Return transaction details, like sender address
        '''
        raw_transaction = self.getRawTransaction()
        
        if self['category'] == 'receive':
            sender_address = self.decodeScriptSig(raw_transaction, self['currency'], self['wallet'].getNet())
        else:
            sender_address = None
            
        return {'sender_address': sender_address}
    
    def getRawTransaction(self):
        '''
        Get the raw transaction dict
        '''
        cache_hash = self.getParamHash("details")
        cached_object = self._cache.fetch('details', cache_hash)
        if cached_object:
            raw_transaction = cached_object
        else:
            raw_transaction = connections.connector.getRawTransaction(self['txid'], self['wallet']['provider_id'])
            self._cache.store('details', cache_hash, raw_transaction)
        return raw_transaction

    def getSenderAddress(self):
        '''
        Getter function for the sender address
        '''
        if self['category'] == 'receive':
            meta_properties = self.metaProperties()
            if meta_properties.get('sender_address', False):
                return CoinAddress(meta_properties['sender_address'], 'This is a sender address!')
            
        return None

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
    