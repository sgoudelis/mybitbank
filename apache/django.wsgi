import os
import sys

path = os.path.dirname(os.path.abspath(__file__))+'/../'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mybitbank.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
