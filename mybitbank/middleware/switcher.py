import datetime

from django.utils.timezone import utc
from mybitbank.libs.jsonrpc import ServiceProxy
from mybitbank.libs.connections import connector


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
                    connector.alerts[:] = [m for m in connector.alerts if m.get('type', None) == 'currencybackend' and m.get('provider_id', None) != provider_id]
            
        return None
    
    def process_response(self, request, response):
        '''
        Clear connector errors after the view has been compiled
        '''
        connector.errors = []
        
        return response
    