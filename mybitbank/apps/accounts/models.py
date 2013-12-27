from django.db import models


class accountFilter(models.Model):
    '''
    status 1 = archived
    status 2 = hidden
    '''
    address = models.CharField(max_length=200)
    currency = models.CharField(max_length=3)
    name = models.CharField(max_length=200)
    status = models.IntegerField()
    entered = models.DateTimeField('date published')

class addressAliases(models.Model):
    '''
    model for address aliases
    '''
    address = models.CharField(max_length=200, unique=False)
    alias = models.CharField(max_length=200)
    status = models.IntegerField()
    entered = models.DateTimeField('date published')
    
    