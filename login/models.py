from django.db import models
from django.contrib.auth.models import User
from login.settings import UserSettings

class Setting(models.Model):
    user = models.ForeignKey(User, unique=False)
    name = models.CharField(max_length=200, unique=True)
    value = models.CharField(max_length=200)
    
# attach a UserSettings object in the User object
User.setting = property(lambda u: UserSettings(user=u))
