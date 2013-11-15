import datetime
from accounts.models import addressAliases

class CoinAddress(str):
    '''
    Class for addresses
    '''
    aliases = []
    hidden = False
    archived = False
    
    def __init__(self, string):
        # call the str constructor
        super(CoinAddress, self).__init__(string)
        
        # fill in the aliases
        self.aliases = addressAliases.objects.filter(address=string, status__gt=1)

    def setAlias(self, alias):
        # set the alias in the db
        if alias:
            self.aliases.append(alias)
            newaddralias = addressAliases.objects.create(address=str(self), alias=alias, status=2, entered=datetime.datetime.utcnow())
            return newaddralias
        else:
            return False
        
        