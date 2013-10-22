from django.test import TestCase
from decimal import Decimal
from connections import Connector
#import generic

rawData = {
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
        
        #generic.prettyPrint(accounts)
        
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
        
    def test_moveamount_nonexistant_from_account(self):
        '''
        Test moveamount() method testing non-existant from account
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
        Test moveamount() method testing non-existant from account
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
        Test moveamount() method testing non-existant from account
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
        Test moveamount() method testing non-existant from account
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
        Test moveamount() method testing non-existant from account
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
        Test moveamount() method testing non-existant from account
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
        Test moveamount() method testing non-existant from account
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
        Test sendfrom() method testing non-existant from account
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
        Test sendfrom() method testing non-existant from account
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
        Test sendfrom() method testing non-existant from account
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
        Test sendfrom() method testing non-existant from account
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
        Test sendfrom() method testing non-existant from account
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
        Test sendfrom() method testing non-existant from account
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
        Test sendfrom() method testing non-existant from account
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        currency = 'btc'
        amount = u""
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendfrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
        
        
        