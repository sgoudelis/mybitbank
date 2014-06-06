import StringIO
import io

from mybitbank.libs.misc.stubconnector import ServiceProxyStubBTC, ServiceProxyStubBTCWithPass
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import setup_test_environment
from lxml import etree

from mybitbank.libs.connections import connector

class TransferIndexTests(TestCase):
    def setUp(self):
        setup_test_environment()
        connector.services = {1: ServiceProxyStubBTC()}
        connector.config = {1: {'id': int(1),
                             'rpcusername': "testuser",
                             'rpcpassword': "testnet",
                             'rpchost': "localhost",
                             'rpcport': "7000",
                             'name': 'Bitcoin (BTC)',
                             'currency': 'btc',
                             'symbol': "B",
                             'code': 'BTC',
                             'network': "testnet",
                             'enabled': True,
                           }, }
            
        connector.alerts = {}
        
        user = User.objects.create_user('testing', 'testing@testingpipes.com', 'testingpassword')
        user.save()

    def stripHeaders(self, response):
        '''
        String the HTTP headers of the response
        '''
        html_response = ""
        line_no = 0
        io_response = io.BytesIO(str(response))
        for i, line in enumerate(io_response, 1):
            if "DOCTYPE" in line:
                line_no = i
                
        io_response.seek(0)
        with io_response as f:
            html_list = f.readlines()[(line_no - 1):]

        return html_response.join(html_list)

    def validateHTML(self, html):
        try:
            parser = etree.HTMLParser(recover=True)
            tree = etree.parse(StringIO.StringIO(html), parser)
            return tree
        except:
            raise
            return False

    def test_index_account_menus(self):
        '''
        Test if there are accounts in the dropdownmenus
        '''
        
        client = Client()
        client.login(username='testing', password='testingpassword')
        response = client.get(reverse('transfer:index'))
        response_html = self.stripHeaders(response)
        html_tree = self.validateHTML(response_html)

        # validate HTML
        self.assertNotEquals(html_tree, False)
        
        from_account_options = html_tree.xpath("//select[@id='from_account']/option")
        to_account_options = html_tree.xpath("//select[@id='to_account']/option")

        self.assertEquals(len(from_account_options), 7)
        self.assertEquals(len(to_account_options), 7)
        
    def test_tranfer_submit_XSRF_failure(self):
        '''
        Test XSRF errors come out an empty POST
        '''
        
        provider_id = 1
        client = Client(enforce_csrf_checks=True)
        client.login(username='testing', password='testingpassword')
        
        post_data = {
                    'amount': "",
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "",
                    'provider_id': provider_id,
                    'to_address': ""
                    }
        
        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        
        self.assertContains(response, '403', status_code=403)
        
    def test_tranfer_submit_empty_values(self):
        '''
        Test empty form submittion
        '''
        
        provider_id = 1
        client = Client()
        client.login(username='testing', password='testingpassword')
        
        post_data = {
                    'amount': "",
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "",
                    'provider_id': provider_id,
                    'to_address': ""
                    }
        
        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        response_html = self.stripHeaders(response)
        html_tree = self.validateHTML(response_html)

        # validate HTML
        self.assertNotEquals(html_tree, False)
        
        self.assertNotEquals(html_tree.xpath('//*[@id="error_message_from_account"]'), []) 
        self.assertNotEquals(html_tree.xpath('//*[@id="error_message_to_address"]'), [])
        self.assertNotEquals(html_tree.xpath('//*[@id="error_message_amount"]'), [])
        
    def test_tranfer_submit_with_from_account_value(self):
        '''
        Test with from address value only
        '''
        
        provider_id = 1
        client = Client()
        client.login(username='testing', password='testingpassword')
        
        post_data = {
                    'amount': "",
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "23a3862ba3a94184560b6fa5a5d137573122df20",
                    'provider_id': provider_id,
                    'to_address': ""
                    }
        
        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        response_html = self.stripHeaders(response)
        html_tree = self.validateHTML(response_html)

        # validate HTML
        self.assertNotEquals(html_tree, False)
        
        self.assertNotEquals(html_tree.xpath('//*[@id="error_message_to_address"]'), [])
        self.assertNotEquals(html_tree.xpath('//*[@id="error_message_amount"]'), [])
       
    def test_tranfer_submit_with_to_account_value(self):
        '''
        Test with to address value only
        '''
        
        provider_id = 1
        client = Client()
        client.login(username='testing', password='testingpassword')
        
        post_data = {
                    'amount': "",
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "",
                    'provider_id': 1,
                    'to_address': "mox7nxwfu9hrTQCn24RBTDce1wiHEP1NQp"
                    }
        
        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        response_html = self.stripHeaders(response)
        html_tree = self.validateHTML(response_html)

        # validate HTML
        self.assertNotEquals(html_tree, False)
        
        self.assertNotEquals(html_tree.xpath('//*[@id="error_message_from_account"]'), [])
        self.assertNotEquals(html_tree.xpath('//*[@id="error_message_amount"]'), []) 
        
    def test_tranfer_submit_with_from_to_values(self):
        '''
        Test with from/to addresses without amount
        '''
        
        provider_id = 1
        client = Client()
        client.login(username='testing', password='testingpassword')
        
        post_data = {
                    'amount': "",
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "23a3862ba3a94184560b6fa5a5d137573122df20",
                    'provider_id': provider_id,
                    'to_address': "mox7nxwfu9hrTQCn24RBTDce1wiHEP1NQp"
                    }
        
        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        response_html = self.stripHeaders(response)
        html_tree = self.validateHTML(response_html)

        # validate HTML
        self.assertNotEquals(html_tree, False)
        
        self.assertNotEquals(html_tree.xpath('//*[@id="error_message_amount"]'), []) 
        
    def test_tranfer_submit_with_from_to_same_values(self):
        '''
        Test same address for from and to
        '''
        
        provider_id = 1
        client = Client()
        client.login(username='testing', password='testingpassword')
        
        post_data = {
                    'amount': "",
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "23a3862ba3a94184560b6fa5a5d137573122df20",
                    'selected_currency': "btc",
                    'to_address': "mxgWFbqGPywQUKNXdAd3G2EH6Te1Kag5MP"
                    }
        
        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        response_html = self.stripHeaders(response)
        html_tree = self.validateHTML(response_html)

        # validate HTML
        self.assertNotEquals(html_tree, False)
        
        self.assertNotEquals(html_tree.xpath("/html/body/div/form/div/div[2]/div[2]/strong/ul[@class='errorlist']"), []) 
        
    def test_tranfer_submit_with_correct_values_move(self):
        '''
        Test correct value -> move
        '''
        
        provider_id = 1
        client = Client()
        client.login(username='testing', password='testingpassword')
        
        post_data = {
                    'amount': 1,
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "23a3862ba3a94184560b6fa5a5d137573122df20",
                    'provider_id': provider_id,
                    'to_account': "mox7nxwfu9hrTQCn24RBTDce1wiHEP1NQp",
                    'to_address': "mox7nxwfu9hrTQCn24RBTDce1wiHEP1NQp"
                    }
        
        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        self.assertContains(response, text='', count=None, status_code=302)
        
    def test_tranfer_submit_test_invalid_provider_id(self):
        '''
        Test invalid provider_id
        '''
        
        provider_id = 9
        client = Client()
        client.login(username='testing', password='testingpassword')
        
        post_data = {
                    'amount': 1,
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "23a3862ba3a94184560b6fa5a5d137573122df20",
                    'provider_id': provider_id,
                    'to_address': "mox7nxwfu9hrTQCn24RBTDce1wiHEP1NQp"
                    }

        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        response_html = self.stripHeaders(response)
        html_tree = self.validateHTML(response_html)

        # validate HTML
        self.assertNotEquals(html_tree, False)
        self.assertNotEquals(html_tree.xpath("/html/body/div/form/div/div[2]/div[2]/strong/ul[@class='errorlist']"), [])
    
    def test_tranfer_submit_invalid_from_account(self):
        '''
        Test invalid address
        '''
        
        provider_id = 1
        client = Client()
        client.login(username='testing', password='testingpassword')
        
        post_data = {
                    'amount': 3,
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "23a3862PIPIPPIPIES5a5d137573122df20",
                    'provider_id': provider_id,
                    'to_address': "mox7nxwfu9hrTQCn24RBTDce"
                    }

        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        response_html = self.stripHeaders(response)
        html_tree = self.validateHTML(response_html)

        # validate HTML
        self.assertNotEquals(html_tree, False)

        self.assertNotEquals(html_tree.xpath('//*[@id="error_message_to_address"]'), [])
        
    def test_tranfer_submit_required_pass(self):
        '''
        Test requiring passphrase
        '''
        
        provider_id = 1
        client = Client()
        client.login(username='testing', password='testingpassword')
        
        connector.services = {provider_id: ServiceProxyStubBTCWithPass()}
        
        post_data = {
                    'amount': 3,
                    'comment': "",
                    'comment_to': "",
                    'csrfmiddlewaretoken': "",
                    'from_account': "23a3862ba3a94184560b6fa5a5d137573122df20",
                    'provider_id': provider_id,
                    'to_address': "mzPYZFvH61gvEwXShHGY9WUEQG1WCSKshv"
                    }

        response = client.post(reverse('transfer:send', kwargs={'selected_provider_id': provider_id}), post_data)
        response_html = self.stripHeaders(response)
        html_tree = self.validateHTML(response_html)
        #print response_html
        # validate HTML
        self.assertNotEquals(html_tree, False)
        self.assertNotEquals(html_tree.xpath("//*[@id='passphrase']"), [])
