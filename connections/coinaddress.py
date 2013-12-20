import datetime
from accounts.models import addressAliases
from addressbook.models import savedAddress
from django.utils.timezone import utc

class CoinAddress(object):
    '''
    Class for addresses
    '''
    _address = None
    _aliases = []
    
    def __init__(self, address):
        '''
        Initialize CoinAddress object
        '''
        super(CoinAddress, self).__init__()
        self._address = address
        
        # fill in the aliases
        self._aliases = addressAliases.objects.filter(address=address, status__gt=1)

    def __str__(self):
        '''
        String representation of this CoinAddress
        '''
        return str(self._address)
    
    def __unicode__(self):
        '''
        Unicode representation of this CoinAddress
        '''
        return unicode(self._address)

    def setAlias(self, alias):
        '''
        Set the alias in the db
        '''
        if alias:
            self._aliases.append(alias)
            newaddralias = addressAliases.objects.create(address=str(self), alias=alias, status=2, entered=datetime.datetime.utcnow().replace(tzinfo=utc))
            return newaddralias
        else:
            return False
        
    def getAddressBookName(self):
        '''
        Get the addressbook name entry if there is one. Perhaps not cached. Look up later
        '''
        try:
            addressBookAddress = savedAddress.objects.filter(status__gt=1, address=self)
            # get the first one for now
            return addressBookAddress[0].name
        except:
            return False
        
        