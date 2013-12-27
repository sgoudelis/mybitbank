import datetime

from django.utils.timezone import utc

from mybitbank.libs.connections import connector


class SSLChecker():
    '''
    This middleware class with set/clear an alert about non-existing SSL
    '''
    def process_request(self, request):
        if request.is_secure():
            # clear alert about non-existing SSL
            connector.alerts['sslchecker'] = []
        else:
            if connector.alerts.get('sslchecker', True) is True:
                # add alert about non-existing SSL
                connector.addAlert('sslchecker', {'message': 'You are currently not secure. No HTTPS/SSL connection detected!', 'when': datetime.datetime.utcnow().replace(tzinfo=utc)})
