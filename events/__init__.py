import datetime
from models import Events
from django.utils.timezone import utc

def addEvent(request, description='no description', level='info'):
    '''
    Add an Event in the database
    '''
    
    if request:
        user_id = request.user.id
    else:
        return None
    
    if level in ['info', 'debug', 'warning', 'alert', 'error']:
        event = Events.objects.create(user_id=user_id, description=description, level=level, entered=datetime.datetime.utcnow().replace(tzinfo=utc))
        event.save()
    