import connections
import datetime
from jsonrpc import ServiceProxy

class CurrencyEnabler():
    '''
    Re-enable currency service after time has elapsed. This is a Django middleware.
    '''
    
    def process_request(self, request):
        '''
        Before the view is compiled, re-enabled disabled currency services.
        
        '''
        
        '''
        # remove all switcher alerts
        connections.connector.errors[:] = [m for m in connections.connector.errors if m.get('type', None) != 'switcher']
        
        for currency in connections.connector.config.keys():
            if connections.connector.config[currency]['enabled'] not in (True, False):
                # assume the value is datetime in the future... or is it ?
                if datetime.datetime.utcnow() >= connections.connector.config[currency]['enabled']:
                    # re-enable currency service
                    connections.connector.services[currency] = ServiceProxy("http://%s:%s@%s:%s" % (connections.connector.config[currency]['rpcusername'], 
                                                                                   connections.connector.config[currency]['rpcpassword'], 
                                                                                   connections.connector.config[currency]['rpchost'], 
                                                                                   connections.connector.config[currency]['rpcport']))
                    connections.connector.config[currency]['enabled'] = True
                    print "re-enabled %s" % currency
                else:
                    print 
                    connections.connector.errors.append({'type': 'switcher', 'currency': currency, 'message': 'Currency service for %s is disabled for another %s secs' % (currency.upper(), connections.connector.config[currency]['enabled']-datetime.datetime.utcnow()), 'when': datetime.datetime.utcnow()})
            elif connections.connector.config[currency]['enabled'] is False:
                # put a disabled message 
                print "permenetly disabled %s" % currency
                connections.connector.errors.append({'type': 'switcher', 'currency': currency, 'message': 'Currency service for %s is disabled temporarely' % (currency.upper()), 'when': datetime.datetime.utcnow()})
            elif connections.connector.config[currency]['enabled'] is True:
                # remove standing error from the list
                print "remove standing error from the list"
                connections.connector.errors[:] = [m for m in connections.connector.errors if m.get('type', None) == 'switcher' and m.get('currency', None) != currency]
        '''
        
        # just re-enable the service
        for currency in connections.connector.config.keys():
            if connections.connector.config[currency]['enabled'] not in (True, False):
                # assume the value is datetime in the future... or is it ?
                if datetime.datetime.utcnow() >= connections.connector.config[currency]['enabled']:
                    # re-enable currency service
                    connections.connector.services[currency] = ServiceProxy("http://%s:%s@%s:%s" % (connections.connector.config[currency]['rpcusername'], 
                                                                                   connections.connector.config[currency]['rpcpassword'], 
                                                                                   connections.connector.config[currency]['rpchost'], 
                                                                                   connections.connector.config[currency]['rpcport']))
                    connections.connector.config[currency]['enabled'] = True
                    connections.connector.alerts[:] = [m for m in connections.connector.alerts if m.get('type', None) == 'currencybackend' and m.get('currency', None) != currency]
        return None
    
    
    def process_response(self, request, response):
        '''
        Clear connector erros after the view has been compiled
        '''
        connections.connector.errors = []
        
        return response
    