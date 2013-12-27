from django.db import models


class savedAddress(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    currency = models.CharField(max_length=200)
    comment = models.CharField(max_length=500)
    status = models.IntegerField()
    entered = models.DateTimeField('date published')
    
    
