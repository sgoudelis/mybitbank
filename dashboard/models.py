from django.db import models
from django.contrib.auth.models import User

class Events(models.Model):
    user = models.ForeignKey(User, unique=False)
    description = models.CharField(max_length=1000)
    level = models.CharField(max_length=12)
    entered = models.DateTimeField('date published')
    