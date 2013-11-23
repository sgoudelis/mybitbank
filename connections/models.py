from django.db import models

class CurrencyService(models.Model):
    '''
    model for address aliases
    '''
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    rpcusername = models.CharField(max_length=200)
    rpcpassword = models.CharField(max_length=200)
    rpchost = models.CharField(max_length=200)
    rpcport = models.CharField(max_length=200)
    entered = models.DateTimeField('date published')
    