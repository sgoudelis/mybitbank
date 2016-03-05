"""
The MIT License (MIT)

Copyright (c) 2016 Stratos Goudelis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

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
