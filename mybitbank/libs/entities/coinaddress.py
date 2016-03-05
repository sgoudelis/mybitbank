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
from mybitbank.apps.accounts.models import addressAliases
from mybitbank.apps.addressbook.models import savedAddress


class CoinAddress(object):
    '''
    Class for addresses
    '''
    
    def __init__(self, address, account):
        '''
        Initialize CoinAddress object
        '''
        
        super(CoinAddress, self).__init__()
        self._address = None
        self._aliases = []
        self._address = address
        self._account = account
        
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
    
    @property
    def alias(self):
        '''
        Return the first alias only
        '''
        aliases = self.getAliases()
        if aliases:
            return aliases[0].alias

    def getAliases(self):
        '''
        Return a list of aliases this address has
        '''
        return self._aliases
    
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
        
    def getAccount(self):
        '''
        Return account object
        '''
        return self._account
        
