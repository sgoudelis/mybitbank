from mybitbank.libs.misc.stubconnector import rawData, ServiceProxyStubBTC
from django.contrib.auth.models import User
from django.test import TestCase
from mybitbank.libs.connections.connectors import Connector


class ConnectorsTests(TestCase):
    connector = None

    def setUp(self):
        '''
        Setup the test
        '''
        self.connector = Connector()
        self.connector.services = {1: ServiceProxyStubBTC()}
        self.connector.config = {1: {'id': int(1),
                                     'rpcusername': "testuser",
                                     'rpcpassword': "testnet",
                                     'rpchost': "localhost",
                                     'rpcport': "7000",
                                     'name': 'Bitcoin (BTC)',
                                     'currency': 'btc',
                                     'symbol': "B",
                                     'enabled': True,
                                   }, }
        
        user = User.objects.create_user('testing', 'testing@testingpipes.com', 'testingpassword')
        user.save()
        
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
        
    def test_listAccounts(self):
        '''
        Test listAccounts() method
        '''
        accounts = self.connector.listAccounts(gethidden=True, getarchived=True)
        provider_id = 1
        
        # check number of in and out accounts        
        number_raw_accounts = len(self.connector.services[provider_id].listaccounts().keys())
        number_processed_accounts = len(accounts[provider_id])
        
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
        provider_id = 1
        addresses = self.connector.services[provider_id].getaddressesbyaccount(account_name)

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
        provider_id = 1
        addresses = self.connector.services[provider_id].getaddressesbyaccount(account_name)
        self.assertTrue(addresses is False, 'Connector.getaddressesbyaccount() method error, wrong address returned')
        
    def test_listTransactionsByAccount(self):
        '''
        Test listTransactionsByAccount() method
        '''
        
        accoount_name = "pipes"
        provider_id = 1
        transactions = self.connector.listTransactionsByAccount(accoount_name, provider_id)
        correct_transactions = rawData['transactions']['pipes']
        
        self.assertEquals(transactions, correct_transactions, 'Connector.listtransactions() method returned wrong number of transactions')
        
    def test_getNewAddress(self):
        '''
        Test getnewaddress() method
        '''
        provider_id = 1
        new_address = self.connector.getNewAddress(provider_id, rawData['new_account_address'])
        self.assertEquals(new_address, rawData['new_account_address'])
        
    def test_getnewaddress_invalid_currency(self):
        '''
        Test getnewaddress() method with invalid currency id
        '''
        
        new_address = self.connector.getNewAddress('INV', rawData['new_account_address'])
        self.assertEquals(new_address, False)

    def test_getnewaddress_unicode_account_name(self):
        '''
        Test getnewaddress() method with a unicode string account name
        '''
        
        account_name = u'thisisunicode'
        provider_id = 1
        new_address = self.connector.getNewAddress(provider_id, account_name)
        self.assertEquals(new_address, 'new account address')        
        
    def test_getnewaddress_nonstring_account_name(self):
        '''
        Test getnewaddress() method with invalid currency id
        '''
        
        account_name = False
        provider_id = 1
        new_address = self.connector.getNewAddress(provider_id, account_name)
        self.assertEquals(new_address, None)
        
    def test_getBalance(self):
        '''
        Test getBalance() method
        '''        
        provider_id = 1
        balance = self.connector.getBalance(provider_id, "my test BTC account")
        correct_result = {provider_id: rawData['accounts']['my test BTC account']}
        self.assertEquals(balance, correct_result)
        
    def test_getBalance_all_accounts(self):
        '''
        Test getBalance() method, return all accounts
        '''        
        provider_id = 1
        balance = self.connector.getBalance(provider_id)
        correct_result = {provider_id: rawData['accounts']}
        self.assertEquals(balance, correct_result)
        
    def test_moveamount(self):
        '''
        Test moveamount() method
        '''
        
        from_account = "pipes"
        to_account = "another account"
        provider_id = 1
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveAmount(from_account, to_account, provider_id, amount, minconf, comment)
        self.assertEquals(move_result, True)
        
    def test_moveamount_nonexisting_from_account(self):
        '''
        Test moveamount() method testing non-existing from account
        '''
        
        from_account = "Idontexistretsakalia"  # non-existing account
        to_account = "another account"
        provider_id = 1
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveAmount(from_account, to_account, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_moveamount_nonexistant_to_account(self):
        '''
        Test moveamount() method testing non-existing to account
        '''
        
        from_account = "pipes"
        to_account = "Idontexistretsakalia"
        provider_id = 0
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveAmount(from_account, to_account, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
       
    def test_moveamount_invalid_currency(self):
        '''
        Test moveamount() method testing invalid currency
        '''
        
        from_account = "pipes"
        to_account = "another account"
        provider_id = 0
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveAmount(from_account, to_account, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
         
    def test_moveamount_non_number_amount_1(self):
        '''
        Test moveamount() method testing non-number amount
        '''
        
        from_account = "pipes"
        to_account = "another account"
        provider_id = 1
        amount = {}
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveAmount(from_account, to_account, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_moveamount_non_number_amount_2(self):
        '''
        Test moveamount() method testing non-number amount
        '''
        
        from_account = "pipes"
        to_account = "another account"
        provider_id = 1
        amount = True
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveAmount(from_account, to_account, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)

    def test_moveamount_non_number_amount_3(self):
        '''
        Test moveamount() method testing non-number amount
        '''
        
        from_account = "pipes"
        to_account = "another account"
        provider_id = 1
        amount = ""
        minconf = 1
        comment = "test comment from django test"

        move_result = self.connector.moveAmount(from_account, to_account, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_moveamount_non_number_amount_4(self):
        '''
        Test moveamount() method testing non-number amount
        '''
        
        from_account = "pipes"
        to_account = "another account"
        provider_id = 1
        amount = u""
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.moveAmount(from_account, to_account, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_sendFrom_nonexistant_from_account(self):
        '''
        Test sendFrom() method testing non-existing from account
        '''
        
        from_account = "Idontexistretsakalia"
        address = "address for sdfsdfs account"
        currency = 'btc'
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendFrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_sendFrom_nonexistant_address(self):
        '''
        Test sendFrom() method testing non-existing address
        '''
        
        from_account = "pipes"
        address = "Idontexistretsakalia"
        currency = 'btc'
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendFrom(from_account, address, currency, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
       
    def test_sendFrom_invalid_currency(self):
        '''
        Test sendFrom() method testing invalid currency
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        provider_id = 0
        amount = "1"
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendFrom(from_account, address, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_sendFrom_non_number_amount_1(self):
        '''
        Test sendFrom() method testing non-number amount
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        provider_id = 1
        amount = {}
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendFrom(from_account, address, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)

    def test_sendFrom_non_number_amount_3(self):
        '''
        Test sendFrom() method testing non-number amount
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        provider_id = 1
        amount = ""
        minconf = 1
        comment = "test comment from django test"

        move_result = self.connector.sendFrom(from_account, address, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_sendFrom_non_number_amount_4(self):
        '''
        Test sendFrom() method testing non-number amount
        '''
        
        from_account = "pipes"
        address = "address for sdfsdfs account"
        provider_id = 1
        amount = u""
        minconf = 1
        comment = "test comment from django test"
        
        move_result = self.connector.sendFrom(from_account, address, provider_id, amount, minconf, comment)
        self.assertNotEquals(move_result, True)
        
    def test_walletpassphrase_invalid_passphrase_1(self):
        '''
        Test unload wallet
        '''
        
        passphrase = True
        provider_id = 1
        
        unlock_exit = self.connector.walletPassphrase(passphrase, provider_id)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_passphrase_2(self):
        '''
        Test unload wallet
        '''
        
        passphrase = {}
        provider_id = 1
        
        unlock_exit = self.connector.walletPassphrase(passphrase, provider_id)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_passphrase_3(self):
        '''
        Test unload wallet
        '''
        
        passphrase = None
        provider_id = 1
        
        unlock_exit = self.connector.walletPassphrase(passphrase, provider_id)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_passphrase_4(self):
        '''
        Test unload wallet
        '''
        
        passphrase = ""
        provider_id = 1
        
        unlock_exit = self.connector.walletPassphrase(passphrase, provider_id)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_currency_1(self):
        '''
        Test unload wallet
        '''
        
        passphrase = "testpassphrase"
        provider_id = 'inv'
        
        unlock_exit = self.connector.walletPassphrase(passphrase, provider_id)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_currency_2(self):
        '''
        Test unload wallet
        '''
        
        passphrase = "testpassphrase"
        provider_id = ""
        
        unlock_exit = self.connector.walletPassphrase(passphrase, provider_id)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletpassphrase_invalid_currency_3(self):
        '''
        Test unload wallet
        '''
        
        passphrase = "testpassphrase"
        provider_id = False
        
        unlock_exit = self.connector.walletPassphrase(passphrase, provider_id)
        
        self.assertNotEquals(unlock_exit, True)
        
    def test_walletlock_invalid_currency_1(self):
        '''
        Test walletLock()
        '''
        
        provider_id = "pip"
        lock_exit = self.connector.walletLock(provider_id)
        
        self.assertNotEquals(lock_exit, True)
        
    def test_walletlock_invalid_currency_2(self):
        '''
        Test walletLock()
        '''
        
        provider_id = ""
        lock_exit = self.connector.walletLock(provider_id)
        
        self.assertNotEquals(lock_exit, True)
        
    def test_walletlock_invalid_currency_3(self):
        '''
        Test walletLock()
        '''
        
        provider_id = False
        lock_exit = self.connector.walletLock(provider_id)
        
        self.assertNotEquals(lock_exit, True)
        
    def test_getTransaction(self):
        '''
        Test getTransaction()
        '''

        correct_transaction = rawData['transactions']['pipes'][0]
        txid = correct_transaction['txid']
        provider_id = 1
        transaction = self.connector.getTransaction(txid, provider_id)
        self.assertEquals(transaction, correct_transaction)
        
    def test_getTransaction_invalid_provider_id_1(self):
        '''
        Test getTransaction() with invalid provider_id
        '''

        transaction = rawData['transactions']['pipes'][0]
        txid = transaction['txid']
        provider_id = 0
        
        transaction = self.connector.getTransaction(txid, provider_id)
        self.assertNotEquals(transaction.get('code', None), None)

    def test_getTransaction_invalid_provider_id_2(self):
        '''
        Test getTransaction() with invalid provider_id
        '''

        transaction = rawData['transactions']['pipes'][0]
        txid = transaction['txid']
        provider_id = None
        
        transaction = self.connector.getTransaction(txid, provider_id)
        self.assertNotEquals(transaction.get('code', None), None)
        
    def test_getTransaction_invalid_txid_1(self):
        '''
        Test getTransaction() with invalid txid
        '''

        txid = "otinanai"
        provider_id = 1
        
        transaction = self.connector.getTransaction(txid, provider_id)
        self.assertNotEquals(transaction, None)
    
    def test_gettransactiondetails_invalid_txid_2(self):
        '''
        Test gettransactiondetails()
        '''

        txid = False
        provider_id = 1
        
        transaction = self.connector.getTransaction(txid, provider_id)
        self.assertNotEquals(transaction, None)
