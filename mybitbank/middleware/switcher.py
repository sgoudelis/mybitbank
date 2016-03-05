"""
The MIT License (MIT)

Copyright (c) 2016 Stratos Goudelis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import datetime

from django.utils.timezone import utc

from mybitbank.libs.connections import connector
from mybitbank.libs.jsonrpc import ServiceProxy


class CurrencyEnabler():
    '''
    Re-enable currency service after time has elapsed. This is a Django middleware.
    '''
    
    def process_request(self, request):
        '''
        Before the view is compiled, re-enabled disabled currency services.
        '''

        # just re-enable the service
        for provider_id in connector.config.keys():
            if isinstance(connector.config[provider_id].get('enabled', None), datetime.datetime):
                # assume the value is datetime in the future... or is it ?
                if datetime.datetime.utcnow().replace(tzinfo=utc) >= connector.config[provider_id]['enabled']:
                    # re-enable currency service
                    connector.services[provider_id] = ServiceProxy("http://%s:%s@%s:%s" % 
                                                                                  (connector.config[provider_id]['rpcusername'],
                                                                                   connector.config[provider_id]['rpcpassword'],
                                                                                   connector.config[provider_id]['rpchost'],
                                                                                   connector.config[provider_id]['rpcport']))
                    connector.config[provider_id]['enabled'] = True
                    connector.alerts['currencybackend'][:] = [alert for alert in connector.alerts['currencybackend'] if alert.get('provider_id') != provider_id]
            
        return None
    
    def process_response(self, request, response):
        '''
        Clear connector errors after the view has been compiled
        '''
        connector.errors = []
        
        return response
