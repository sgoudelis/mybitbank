import datetime

from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.utils.timezone import utc

from models import Events


def addEvent(request, description='no description', level='info'):
    '''
    Add an Event in the database
    '''
    
    if isinstance(request, WSGIRequest):
        # get the user id from the request object
        user_id = request.user.id
    elif type(request) in [str, unicode]:
        # assume it is a username
        try:
            user_id = User.objects.get(username=request).id
        except:
            user_id = User.objects.get(id=1).id
    
    try:
        if level in ['info', 'debug', 'warning', 'alert', 'error']:
            event = Events.objects.create(user_id=user_id, description=description, level=level, entered=datetime.datetime.utcnow().replace(tzinfo=utc))
            event.save()
    except:
        return None
    