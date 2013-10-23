from django.test import TestCase
from decimal import Decimal
from connections import Connector
# import generic

rawData = {
           'passphrase': 'testpassphrase',
           'new_account_address': "new account address",
           'accounts': {
                        u'': Decimal('0.00000000'),
                        u'pipes': Decimal('0E-8'),
                        u'another account': Decimal('0E-8'),
                        u'my empty account': Decimal('0E-8'),
                        u'my test BTC account': Decimal('230.00000000'),
                        u'sdfsdfs': Decimal('0E-8')
                        },
           
           'addresses': {
                       u'': ['address for default account'],
                       u'pipes': ['address for pipes account', 'second address for pipes account'],
                       u'another account': ['address for another account'],
                       u'my empty account': ['address for empty account'],
                       u'my test BTC account': ['address for my test BTC account'],
                       u'sdfsdfs': ['address for sdfsdfs account'],
                       },
           'transactions': {
                           u'': [{
                                    "account" : "",
                                    "address" : "address for default account",
                                    "category" : "receive",
                                    "amount" : 15.60073559,
                                    "confirmations" : 5944,
                                    "blockhash" : "0000000000000009b4bec9a4374031762c7c9700eab2a9442336712fc769d7e7",
                                    "blockindex" : 427,
                                    "blocktime" : 1379839630,
                                    "txid" : "9599c2c44e1be0001ad8c03038b50b47e634329917eb6d08f7fc675310075f02",
                                    "time" : 1379839327,
                                    "timereceived" : 1379839327
                                }],
                           u'pipes':  [{
                                            "account" : "pipes",
                                            "address" : "address for pipes account",
                                            "category" : "receive",
                                            "amount" : 12.20073359,
                                            "confirmations" : 5944,
                                            "blockhash" : "0000000000000009b4bec9a4374031762c7c9700eab2a9442336712fc769d7e7",
                                            "blockindex" : 427,
                                            "blocktime" : 1379839630,
                                            "txid" : "9599c2c44e1be0001ad8c03038b50b47e634329917eb6d08f7fc675310075f02",
                                            "time" : 1379839327,
                                            "timereceived" : 1379839327
                                        },
                                       {
                                            "account" : "pipes",
                                            "address" : "address for pipes account",
                                            "category" : "receive",
                                            "amount" : 1.245,
                                            "confirmations" : 345,
                                            "blockhash" : "0000000000000009b4bec9a4374031762c7c9700eab2a9442336712fc769d7e7",
                                            "blockindex" : 427,
                                            "blocktime" : 1379836630,
                                            "txid" : "9599c2c44e1be0001ad8c03038b50b47e634329917eb6d08f7fc675310075f02",
                                            "time" : 1372339327,
                                            "timereceived" : 1379839327
                                        }],
                           u'another account': [],
                           u'my empty account': [],
                           u'my test BTC account': [{
                                                        "account" : "",
                                                        "address" : "address for default account",
                                                        "category" : "receive",
                                                        "amount" : 15.60073559,
                                                        "confirmations" : 5944,
                                                        "blockhash" : "0000000000000009b4bec9a4374031762c7c9700eab2a9442336712fc769d7e7",
                                                        "blockindex" : 427,
                                                        "blocktime" : 1379839630,
                                                        "txid" : "9599c2c44e1be0001ad8c03038b50b47e634329917eb6d08f7fc675310075f02",
                                                        "time" : 1379839327,
                                                        "timereceived" : 1379839327
                                                    }],
                           u'sdfsdfs': [],
                        },
                  'balance': Decimal('30.00000000'),
                  
                  
                  'rawtransactions':  [
                                                {   u'blockhash': u'00000000f623a840f81762114d5426faabeb2fcf8b13e3edb128273aa24a3c38',
                                                        u'blocktime': 1382465670,
                                                        u'confirmations': 73,
                                                        u'hex': u'01000000018419d61304f827e0743e84ce3ae694ac2adbc43ca57c5c8997543eba1b8b9fa4000000006a4730440220475a95f43295daaf6575ee0cd9e576d6d6f95a25e7ca51950f9976f4570f294302206798592cfa435be24e503325b0a11364d61ec0c5aab494049b5d35208ed24edf012103d0b8349514469b2c42b41f2aa8982d4b9a666c1662865bd4728c04ad535739f4ffffffff0260d0bb27000000001976a9146608824a44bf9d4c4c7440227143f9b8283439b388ac9002cc00000000001976a914bc488f1667ee3e8b42bb95e320341689f0c5ffc788ac00000000',
                                                        u'locktime': 0,
                                                        u'time': 1382465670,
                                                        u'txid': u'd1f51c53cc35e14596a6cd3607689927dd1ef0d133037883b7dd85f058ffab73',
                                                        u'version': 1,
                                                        u'vin': [   {   u'scriptSig': {   u'asm': u'30440220475a95f43295daaf6575ee0cd9e576d6d6f95a25e7ca51950f9976f4570f294302206798592cfa435be24e503325b0a11364d61ec0c5aab494049b5d35208ed24edf01 03d0b8349514469b2c42b41f2aa8982d4b9a666c1662865bd4728c04ad535739f4',
                                                                                          u'hex': u'4730440220475a95f43295daaf6575ee0cd9e576d6d6f95a25e7ca51950f9976f4570f294302206798592cfa435be24e503325b0a11364d61ec0c5aab494049b5d35208ed24edf012103d0b8349514469b2c42b41f2aa8982d4b9a666c1662865bd4728c04ad535739f4'},
                                                                        u'sequence': 4294967295,
                                                                        u'txid': u'a49f8b1bba3e5497895c7ca53cc4db2aac94e63ace843e74e027f80413d61984',
                                                                        u'vout': 0}],
                                                        u'vout': [   {   u'n': 0,
                                                                         u'scriptPubKey': {   u'addresses': [   u'mppTQqFFXmk2E4F1FJ5A2BqDt56oYH2Nss'],
                                                                                              u'asm': u'OP_DUP OP_HASH160 6608824a44bf9d4c4c7440227143f9b8283439b3 OP_EQUALVERIFY OP_CHECKSIG',
                                                                                              u'hex': u'76a9146608824a44bf9d4c4c7440227143f9b8283439b388ac',
                                                                                              u'reqSigs': 1,
                                                                                              u'type': u'pubkeyhash'},
                                                                         u'value': Decimal('6.66620000')},
                                                                     {   u'n': 1,
                                                                         u'scriptPubKey': {   u'addresses': [   u'mxgWFbqGPywQUKNXdAd3G2EH6Te1Kag5MP'],
                                                                                              u'asm': u'OP_DUP OP_HASH160 bc488f1667ee3e8b42bb95e320341689f0c5ffc7 OP_EQUALVERIFY OP_CHECKSIG',
                                                                                              u'hex': u'76a914bc488f1667ee3e8b42bb95e320341689f0c5ffc788ac',
                                                                                              u'reqSigs': 1,
                                                                                              u'type': u'pubkeyhash'},
                                                                         u'value': Decimal('0.13370000')}]}
                                                
                                                ]
                                      
           }

class ServiceProxyStubBTC(object):
    def __init__(self):
        self._rawData = rawData
        
    def listaccounts(self):
        return self._rawData['accounts']

    def getaddressesbyaccount(self, account_name):
        try:
            return self._rawData['addresses'][account_name]
        except:
            return False
        
    def listtransactions(self, account_name, count=10, start=0):
        return self._rawData['transactions'][account_name]

    def getnewaddress(self, account_name):
        return self._rawData['new_account_address']
    
    def getbalance(self):
        return self._rawData['balance']
    
    def move(self, from_account, to_account, amount, minconf, comment):
        return True
    
    def sendfrom(self, from_account, to_address, amount, minconf, comment, comment_to):
        return True

    def walletpassphrase(self, passphrase, timeout):
        return True
    
    def walletlock(self):
        return True
    
    def getrawtransaction(self, txid, verbose=1):
        return self._rawData['rawtransaction'][0]


class ConnectorsTests(TestCase):
    connector = None

    def setUp(self):
        self.connector = Connector()
        self.connector.services = {'btc': ServiceProxyStubBTC()}
        
    def test_if_type_object(self):
        '''
        Test instance type
        '''
        self.assertTrue(isinstance(self.connector, Connector), "Instance of connector is not of correct type")
        self.connector = None
        
    def test_longNumber(self):
        '''
        Test longNumber method
        '''
        num = self.connector.longNumber(10)
        self.assertEquals(num, "10.00000000", "Connector.longNumber method is problematic")
        self.connector = None
        
    def test_listaccounts(self):
        '''
        Test listaccounts() method
        '''
        accounts = self.connector.listaccounts(gethidden=True, getarchived=True)
        
        # generic.prettyPrint(accounts)
        
        # check number of in and out accounts        
        number_raw_accounts = len(self.connector.services['btc'].listaccounts().keys())
        number_processed_accounts = len(accounts['btc'])
        
        self.assertEquals(number_raw_accounts, number_processed_accounts, "Connector.listaccounts() method did not deliver correct number of accounts")
        
    def test_getParamHash(self):
        '''
        Test hashing function
        '''
        test_hash = self.connector.getParamHash("test")
        self.assertEquals(test_hash, "90a3ed9e32b2aaf4c61c410eb925426119e1a9dc53d4286ade99a809", "Connector.getParamHash() method is problematic")
       
    def test_getaddressesbyaccount(self):
        '''
        Test getaddressesbyaccount() method
        '''
        account_name = "pipes"
        addresses = self.connector.services['btc'].getaddressesbyaccount(account_name)

        # check number of address        
        self.assertEquals(len(addresses), 2, 'Connector.getaddressesbyaccount() method is not functioning properly, wrong count returned')
        
        # check if addresses contain the "pipes" string
        for address in addresses:
            self.assertTrue(account_name in address, 'Connector.getaddressesbyaccount() method error, wrong address returned')
        
        
    def test_getaddressesbyaccount_no_account_name(self):
        '''
        Test getaddressesbyaccount() method test with no account name
        '''
        account_name = False
        addresses = self.connector.services['btc'].getaddressesbyaccount(account_name)
        self.assertTrue(addresses is False, 'Connector.getaddressesbyaccount() method error, wrong address returned')
        
    def test_listtransactionsbyaccount(self):
        '''
        Test listtransactionsbyaccount() method
        '''
        
        account_name = "pipes"
        transactions = self.connector.listtransactionsbyaccount(account_name, 'btc')
        
        # test number of transactions returned
        number_transactions = len(transactions)
        self.assertEquals(number_transactions, 2, 'Connector.listtransactionsbyaccount() method retured wrong number of transactions')
        
        # test validity of transactions
        for trasnaction in transactions:
            self.assertTrue(account_name in trasnaction['account'], 'Connector.listtransactionsbyaccount() method error, wrong transactions returned')
            self.assertIsNotNone(trasnaction['time_pretty'])
            self.assertIsNotNone(trasnaction['currency'])
            self.assertIsNotNone(trasnaction['timereceived_pretty'])
            self.assertIsNotNone(trasnaction['time_human'])
            self.assertIsNotNone(trasnaction['timereceived_human'])
            self.assertIsNotNone(trasnaction['txid'])
        
    def test_listtransactions(self):
        '''
        Test listtransactions() method
        '''
        
        currency = 'btc'
        transactions = self.connector.listtransactions()
        
        # test number of transactions returned
        number_transactions = len(transactions[currency])
        self.assertEquals(number_transactions, 4, 'Connector.listtransactions() method retured wrong number of transactions')
        
    def test_getnewaddress(self):
        '''
        Test getnewaddress() method
        '''
        
        new_address = self.connector.getnewaddress('btc', rawData['new_account_address'])
        self.assertEquals(new_address, rawData['new_account_address'])
        
    def test_getnewaddress_invalid_currency(self):
        '''
        Test getnewaddress() method with invalid currency id
        '''
        
        new_address = self.connector.getnewaddress('INV', rawData['new_account_address'])
        self.assertEquals(new_address, None)
        
        
    def test_getnewaddress_nonstring_account_name(self):
        '''
        Test getnewaddress() method with invalid currency id
        '''
        
        account_name = False
        new_address = self.connector.getnewaddress('btc', account_name)
        self.assertEquals(new_address, None)
        
    def test_getnewaddress_no_name(self):
        '''
        Test getnewaddress() method with empty name
        '''
        
        new_address = self.connector.getnewaddress('btc', "")
        self.assertEquals(new_address, None)
        
    def test_getbalance(self):
        '''
        Test getbalance() method
        '''        
        
        balance = self.connector.getbalance()
        correct_result = {'btc': self.connector.longNumber(rawData['balance'])}
        self.assertEquals(balance, correct_result)
        
    def test_getaccountdetailsbyaddress(self):
        '''
        Test getaccountdetailsbyaddress() method
        '''
        
        test_account_name = "pipes"
        address = "second address for pipes account"
        account = self.connector.getaccountdetailsbyaddress(address)
        
        self.assertEquals(account['name'], test_account_name)
        
    def test_getaccountdetailsbyaddress_nonexistant_address(self):
        '''
        Test getaccountdetailsbyaddress() method
        '''
        
        address = "otinanaitalegame"
        account = self.connector.getaccountdetailsbyaddress(address)
        
        self.assertEquals(account, None)
        
    def test_getaccountdetailsbyaddress_incorrect_name(self):
        '''
        Test getaccountdetailsbyaddress() method
        '''
        
        test_account_name = "koumoutses"
        address = "second address for pipes account"
        account = self.connector.getaccountdetailsbyaddress(address)
        
        self.assertNotEquals(account['name'], test_account_name)
        
    def test_moveamount(self):
        '''
        Test moveamount() method
        '''
        
        from_account = "pipes"
        to_account = "another account"
        currency = 'btc'
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveamount(from_account, to_account, currency, amount, minconf, comment)
        self.assertEquals(move_result, True)
        
    def test_moveamount_nonexisting_from_account(self):
        '''
        Test moveamount() method testing non-existing from account
        '''
        
        from_account = "Idontexistretsakalia"
        to_account = "another account"
        currency = 'btc'
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveamount(from_account, to_account, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_moveamount_nonexistant_to_account(self):
        '''
        Test moveamount() method testing non-existing to account
        '''
        
        from_account = "pipes"
        to_account = "Idontexistretsakalia"
        currency = 'btc'
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveamount(from_account, to_account, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
       
    def test_moveamount_invalid_currency(self):
        '''
        Test moveamount() method testing invalid currency
        '''
        
        from_account = "pipes"
        to_account = "another account"
        currency = 'INV'
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveamount(from_account, to_account, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
         
    def test_moveamount_non_number_amount_1(self):
        '''
        Test moveamount() method testing non-number amount
        '''
        
        from_account = "pipes"
        to_account = "another account"
        currency = 'btc'
        amount = {}
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveamount(from_account, to_account, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_moveamount_non_number_amount_2(self):
        '''
        Test moveamount() method testing non-number amount
        '''
        
        from_account = "pipes"
        to_account = "another account"
        currency = 'btc'
        amount = True
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveamount(from_account, to_account, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)

    def test_moveamount_non_number_amount_3(self):
        '''
        Test moveamount() method testing non-number amount
        '''
        
        from_account = "pipes"
        to_account = "another account"
        currency = 'btc'
        amount = ""
        minconf = 1
        comment = "test comment from django test"

        move_result = self.connector.moveamount(from_account, to_account, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_moveamount_non_number_amount_4(self):
        '''
        Test moveamount() method testing non-number amount
        '''
        
        from_account = "pipes"
        to_account = "another account"
        currency = 'btc'
        amount = u""
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveamount(from_account, to_account, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_sendfrom_nonexistant_from_account(self):
        '''
        Test sendfrom() method testing non-existing from account
        '''
        
        from_account = "Idontexistretsakalia"
        address = "address for sdfsdfs account"
        currency = 'btc'
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendfrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_sendfrom_nonexistant_address(self):
        '''
        Test sendfrom() method testing non-existing address
        '''
        
        from_account = "pipes"
        address = "Idontexistretsakalia"
        currency = 'btc'
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendfrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
       
    def test_sendfrom_invalid_currency(self):
        '''
        Test sendfrom() method testing invalid currency
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        currency = 'INV'
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendfrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_sendfrom_non_number_amount_1(self):
        '''
        Test sendfrom() method testing non-number amount
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        currency = 'btc'
        amount = {}
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendfrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_sendfrom_non_number_amount_2(self):
        '''
        Test sendfrom() method testing non-number amount
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        currency = 'btc'
        amount = True
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendfrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)

    def test_sendfrom_non_number_amount_3(self):
        '''
        Test sendfrom() method testing non-number amount
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        currency = 'btc'
        amount = ""
        minconf = 1
        comment = "test comment from django test"

        move_result = self.connector.sendfrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_sendfrom_non_number_amount_4(self):
        '''
        Test sendfrom() method testing non-number amount
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        currency = 'btc'
        amount = u""
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendfrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_walletpassphrase_invalid_passphrase_1(self):
        '''
        Test unload wallet
        '''
        
        passphrase = True
        currency = 'btc'
        
        unlock_exit = self.connector.walletpassphrase(passphrase, currency)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_passphrase_2(self):
        '''
        Test unload wallet
        '''
        
        passphrase = {}
        currency = 'btc'
        
        unlock_exit = self.connector.walletpassphrase(passphrase, currency)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_passphrase_3(self):
        '''
        Test unload wallet
        '''
        
        passphrase = None
        currency = 'btc'
        
        unlock_exit = self.connector.walletpassphrase(passphrase, currency)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_passphrase_4(self):
        '''
        Test unload wallet
        '''
        
        passphrase = ""
        currency = 'btc'
        
        unlock_exit = self.connector.walletpassphrase(passphrase, currency)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_currency_1(self):
        '''
        Test unload wallet
        '''
        
        passphrase = "testpassphrase"
        currency = 'inv'
        
        unlock_exit = self.connector.walletpassphrase(passphrase, currency)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_currency_2(self):
        '''
        Test unload wallet
        '''
        
        passphrase = "testpassphrase"
        currency = ""
        
        unlock_exit = self.connector.walletpassphrase(passphrase, currency)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_currency_3(self):
        '''
        Test unload wallet
        '''
        
        passphrase = "testpassphrase"
        currency = False
        
        unlock_exit = self.connector.walletpassphrase(passphrase, currency)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletlock_invalid_currency_1(self):
        '''
        Test walletlock
        '''
        
        currency = "inv"
        lock_exit = self.connector.walletlock(currency)
        
        self.assertNotEquals(lock_exit, True)
        
    def test_walletlock_invalid_currency_2(self):
        '''
        Test walletlock
        '''
        
        currency = ""
        lock_exit = self.connector.walletlock(currency)
        
        self.assertNotEquals(lock_exit, True)
        
    def test_walletlock_invalid_currency_3(self):
        '''
        Test walletlock
        '''
        
        currency = False
        lock_exit = self.connector.walletlock(currency)
        
        self.assertNotEquals(lock_exit, True)
        
    def test_gettransactiondetails(self):
        '''
        Test gettransactiondetails()
        '''

        txid = 'bogus tx id'
        currency = 'btc'
        
        transaction_details = self.connector.gettransactiondetails(txid, currency)
        self.assertEquals(type(transaction_details), dict)
        
    def test_gettransactiondetails_invalid_currency_1(self):
        '''
        Test gettransactiondetails()
        '''

        txid = 'bogus tx id'
        currency = 'inv'
        
        transaction_details = self.connector.gettransactiondetails(txid, currency)
        self.assertNotEquals(transaction_details.get('code', None), None)

    def test_gettransactiondetails_invalid_currency_2(self):
        '''
        Test gettransactiondetails()
        '''

        txid = 'bogus tx id'
        currency = None
        
        transaction_details = self.connector.gettransactiondetails(txid, currency)
        self.assertNotEquals(transaction_details.get('code', None), None)
        
    def test_gettransactiondetails_invalid_txid_1(self):
        '''
        Test gettransactiondetails()
        '''

        txid = {}
        currency = 'btc'
        
        transaction_details = self.connector.gettransactiondetails(txid, currency)
        self.assertNotEquals(transaction_details.get('code', None), None)
    
    def test_gettransactiondetails_invalid_txid_2(self):
        '''
        Test gettransactiondetails()
        '''

        txid = False
        currency = 'btc'
        
        transaction_details = self.connector.gettransactiondetails(txid, currency)
        self.assertNotEquals(transaction_details.get('code', None), None)

    def test_gettransactiondetails_invalid_txid_3(self):
        '''
        Test gettransactiondetails()
        '''

        txid = ""
        currency = 'btc'
        
        transaction_details = self.connector.gettransactiondetails(txid, currency)
        self.assertNotEquals(transaction_details.get('code', None), None)