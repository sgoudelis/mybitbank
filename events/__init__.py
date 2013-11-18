import datetime
from models import Events

def addEvent(request, description='no description', level='info'):
    '''
    Add an Event in the database
    '''
    
    if request:
        user_id = request.user.id
    else:
        user_id = 1
    
    if level in ['info', 'debug', 'warning', 'alert', 'error']:
        event = Events.objects.create(user_id=user_id, description=description, level=level, entered=datetime.datetime.now())
        event.save()
    