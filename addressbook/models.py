from django.db import models

class addressBook(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    status = models.IntegerField()
    entered = models.DateTimeField('date published')
    
    