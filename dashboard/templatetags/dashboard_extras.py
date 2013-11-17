from django import template

def keyvalue(value, arg):
    try:
        return value[arg]
    except:
        return False

def getalerticon(arg):
    
    types = {'info': 'info-sign',
             'alert': 'remove',
             'warning': 'exclamation-sign',
             'success': 'ok'
             }
    return types[arg]

register = template.Library()
register.filter('keyvalue', keyvalue)
register.filter('getalerticon', getalerticon)