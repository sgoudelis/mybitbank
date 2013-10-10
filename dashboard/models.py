from django.db import models

# Create your models here.

class addressbook(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    status = models.IntegerField()
    entered = models.DateTimeField('date published')
    
    