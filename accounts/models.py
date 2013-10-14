from django.db import models

class accountFilter(models.Model):
    address = models.CharField(max_length=200)
    currency = models.CharField(max_length=3)
    name = models.CharField(max_length=200)
    status = models.IntegerField()
    entered = models.DateTimeField('date published')
    
    