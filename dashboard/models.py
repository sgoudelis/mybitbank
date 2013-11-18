from django.db import models

class Events(models.Model):
    description = models.CharField(max_length=1000)
    level = models.CharField(max_length=12)
    entered = models.DateTimeField('date published')
    