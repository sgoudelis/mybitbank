'''
This is WORK-IN-PROGRESS
'''

import models


class UserSettings(object):
    user_id = None
    user_object = None
    
    def __init__(self, user):
        self.user_object = user
        self.user_id = user.id
    
    def set(self, name, value):
        existing = models.Setting.objects.filter(name=name)
        if existing:
            existing.update(value=value)
            return True
        else:
            new_setting = models.Setting(user_id=self.user_id, name=name, value=value)
            new_setting.save()
            return True

    def get(self, name):
        try:
            stored_settings = models.Setting.objects.filter(user_id=self.user_id, name=name)
            if len(stored_settings):
                return stored_settings[0].value
            else:
                return None
        except:
            raise AttributeError('No attribute {0} found !'.format(name))
