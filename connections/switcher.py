import connections
import datetime
from jsonrpc import ServiceProxy
from django.utils.timezone import utc

class CurrencyEnabler():
    '''
    Re-enable currency service after time has elapsed. This is a Django middleware.
    '''
    
    def process_request(self, request):
        '''
        Before the view is compiled, re-enabled disabled currency services.
        '''

        # just re-enable the service
        for provider_id in connections.connector.config.keys():
            if isinstance(connections.connector.config[provider_id].get('enabled', None), datetime.datetime):
                # assume the value is datetime in the future... or is it ?
                if datetime.datetime.utcnow().replace(tzinfo=utc) >= connections.connector.config[provider_id]['enabled']:
                    # re-enable currency service
                    connections.connector.services[provider_id] = ServiceProxy("http://%s:%s@%s:%s" % 
                                                                                  (connections.connector.config[provider_id]['rpcusername'], 
                                                                                   connections.connector.config[provider_id]['rpcpassword'], 
                                                                                   connections.connector.config[provider_id]['rpchost'], 
                                                                                   connections.connector.config[provider_id]['rpcport']))
                    connections.connector.config[provider_id]['enabled'] = True
                    connections.connector.alerts[:] = [m for m in connections.connector.alerts if m.get('type', None) == 'currencybackend' and m.get('provider_id', None) != provider_id]
            
        return None
    
    def process_response(self, request, response):
        '''
        Clear connector errors after the view has been compiled
        '''
        connections.connector.errors = []
        
        return response
    